import json
import re
import urllib.request, urllib.parse
import gradio as gr
from modules import scripts, script_callbacks, shared, ui


def translateGoogle(text, source, target):
    if not text:
        return ""
    params = {
        "sl": source,
        "tl": target,
        "q": text,
    }
    url = f"https://translate.googleapis.com/translate_a/single?dt=t&dt=db&dj=1&client=gtx&{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as res:
        raw = res.read().decode()
        obj = json.loads(raw)
        return obj["sentences"][0]["trans"]


def translateDeepL(text, _, target):
    if not text:
        return ""

    params = {
        "auth_key": shared.opts.translator_deepl_token,
        "text": text,
        "target_lang": target,
    }
    url = (
        "https://api-free.deepl.com/v2/translate"
        if shared.opts.translator_deepl_plan
        else "https://api.deepl.com/v2/translate"
    )
    with urllib.request.urlopen(url + f"?{urllib.parse.urlencode(params)}") as res:
        raw = res.read().decode()
        obj = json.loads(raw)
        return obj["translations"][0]["text"]


class TranslateScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        ctrls = []
        with gr.Group():
            with gr.Accordion("Translator", open=False):
                auto = gr.Checkbox(label="Auto Translation", value=False)
                ctrls.append(auto)
                with gr.Row():
                    source = gr.Textbox(
                        label="Source", value="ja", lines=1, max_lines=1
                    )
                    target = gr.Textbox(
                        label="Target", value="en", lines=1, max_lines=1
                    )
                    app = gr.Radio(
                        ["Google", "DeepL"],
                        value="Google",
                        show_label=False,
                    )
                    ctrls.extend((source, target, app))

                gr.Markdown("---")
                text = gr.TextArea(
                    label="Input",
                    placeholder="Enter text here",
                    show_label=False,
                    lines=2,
                )
                out = gr.TextArea(
                    label="Output",
                    placeholder="Output",
                    interactive=False,
                    show_label=False,
                    lines=2,
                )
                button = gr.Button("Translate", variant="primary")

                button.click(
                    fn=lambda app, *x: (
                        translateGoogle if app == "Google" else translateDeepL
                    )(*x),
                    inputs=[app, text, source, target],
                    outputs=[out],
                )
                ctrls.extend((text, out, button))

            gr.HTML("<br>")

        return ctrls

    def process(self, p, auto, source, target, app, *args):
        if not auto:
            return
        fn = translateGoogle if app == "Google" else translateDeepL
        original_prompt = p.all_prompts[0]
        for i in range(len(p.all_prompts)):
            prompt = p.all_prompts[i]
            p.all_prompts[i] = fn(prompt, source, target)

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Original prompt"] = original_prompt


def on_ui_settings():
    section = ("prompt_translator", "Prompt translator")
    shared.opts.add_option(
        "translator_deepl_token",
        shared.OptionInfo(
            "",
            "DeepL Access Token",
            section=section,
        ),
    )
    shared.opts.add_option(
        "translator_deepl_plan",
        shared.OptionInfo(
            "Free",
            "DeepL plan",
            gr.Radio,
            {"choices": ["Free", "Pro"]},
            section=section,
        ),
    )


script_callbacks.on_ui_settings(on_ui_settings)
