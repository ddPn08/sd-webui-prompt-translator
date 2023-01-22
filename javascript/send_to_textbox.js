function translatorSendToTextBox(tab, neg, text) {
    if (!text) return
    /** @type {HTMLInputElement} */
    const prompt = gradioApp().querySelector(`#${tab}_${neg ? 'neg_' : ''}prompt`).querySelector('textarea')

    prompt.value = prompt.value += `, ${text}`
    prompt.dispatchEvent(new Event('change'))
}