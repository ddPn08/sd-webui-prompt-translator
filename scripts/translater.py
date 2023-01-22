import json
import urllib.request, urllib.parse
from modules import scripts, script_callbacks, shared


class TranslateScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def translatePrompt(self, prompt):
        source = shared.opts.translator_source_language
        target = shared.opts.translator_target_language
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={urllib.parse.quote(source)}&tl={urllib.parse.quote(target)}&dt=t&dt=bd&dj=1&q={urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url) as res:
            raw = res.read().decode()
            obj = json.loads(raw)
            return obj["sentences"][0]["trans"]

    def process(self, p):
        original_prompt = p.all_prompts[0]
        for i in range(len(p.all_prompts)):
            prompt = p.all_prompts[i]
            p.all_prompts[i] = self.translatePrompt(prompt)

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Original prompt"] = original_prompt


def on_ui_settings():
    shared.opts.add_option(
        "translator_source_language",
        shared.OptionInfo(
            "ja",
            "Source language to translate",
            section=("prompt_translator", "Prompt translator"),
        ),
    )
    shared.opts.add_option(
        "translator_target_language",
        shared.OptionInfo(
            "en",
            "Language to translate to",
            section=("prompt_translator", "Prompt translator"),
        ),
    )


script_callbacks.on_ui_settings(on_ui_settings)
