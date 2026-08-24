/** "What do you want to build?" across India's major languages, plus English.
 *
 * The welcome headline cycles through these. Each entry carries its own
 * ``lang``/``dir`` so the browser picks the right script shaping and, for
 * Urdu, flips to right-to-left. ``font-indic`` (see tailwind.config.mjs) puts
 * the Noto Sans script families ahead of the Latin UI font so none of these
 * render as tofu boxes.
 */
export interface WelcomeGreeting {
  /** BCP-47 tag — drives font shaping and screen-reader pronunciation. */
  lang: string;
  /** Native-script rendering of "What do you want to build?" */
  text: string;
  /** Endonym, shown as a subtle caption under the headline. */
  label: string;
  dir?: "ltr" | "rtl";
}

export const WELCOME_GREETINGS: WelcomeGreeting[] = [
  { lang: "en", text: "What do you want to build?", label: "English" },
  { lang: "hi", text: "आप क्या बनाना चाहते हैं?", label: "हिन्दी" },
  { lang: "te", text: "మీరు ఏమి నిర్మించాలనుకుంటున్నారు?", label: "తెలుగు" },
  { lang: "ta", text: "நீங்கள் எதை உருவாக்க விரும்புகிறீர்கள்?", label: "தமிழ்" },
  { lang: "kn", text: "ನೀವು ಏನನ್ನು ನಿರ್ಮಿಸಲು ಬಯಸುತ್ತೀರಿ?", label: "ಕನ್ನಡ" },
  { lang: "mr", text: "तुम्हाला काय तयार करायचे आहे?", label: "मराठी" },
  { lang: "bn", text: "আপনি কী তৈরি করতে চান?", label: "বাংলা" },
  { lang: "gu", text: "તમે શું બનાવવા માંગો છો?", label: "ગુજરાતી" },
  { lang: "ml", text: "നിങ്ങൾ എന്ത് നിർമ്മിക്കാൻ ആഗ്രഹിക്കുന്നു?", label: "മലയാളം" },
  { lang: "pa", text: "ਤੁਸੀਂ ਕੀ ਬਣਾਉਣਾ ਚਾਹੁੰਦੇ ਹੋ?", label: "ਪੰਜਾਬੀ" },
  { lang: "or", text: "ଆପଣ କଣ ତିଆରି କରିବାକୁ ଚାହୁଁଛନ୍ତି?", label: "ଓଡ଼ିଆ" },
  { lang: "ur", text: "آپ کیا بنانا چاہتے ہیں؟", label: "اردو", dir: "rtl" },
];

/** Dwell time per language before cycling to the next. */
export const GREETING_ROTATE_MS = 2600;
