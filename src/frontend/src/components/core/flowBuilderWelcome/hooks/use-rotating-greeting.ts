import { useEffect, useState } from "react";
import {
  GREETING_ROTATE_MS,
  WELCOME_GREETINGS,
  type WelcomeGreeting,
} from "../welcome-greetings";

/** Cycles the welcome headline through India's major languages.
 *
 * Honours ``prefers-reduced-motion``: users who ask for less motion get a
 * single static greeting (English, index 0) instead of a rotating one, since
 * text swapping every couple of seconds is exactly the kind of movement that
 * setting exists to suppress.
 */
export function useRotatingGreeting(): WelcomeGreeting {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    if (reduceMotion) return;

    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % WELCOME_GREETINGS.length);
    }, GREETING_ROTATE_MS);
    return () => window.clearInterval(id);
  }, []);

  return WELCOME_GREETINGS[index];
}
