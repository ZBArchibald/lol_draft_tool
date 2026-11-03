import { useState } from 'react'

const STORAGE_KEY = 'ldt-rotate-hint-dismissed'

function readDismissed(): boolean {
  try {
    return sessionStorage.getItem(STORAGE_KEY) === '1'
  } catch {
    return false // storage blocked (private mode etc.): just show the hint
  }
}

// Asks phone users holding the device upright to rotate it. Pure CSS decides
// visibility (portrait + narrow + touch), so it vanishes the moment they rotate;
// "Continue anyway" hides it for the rest of the session.
export default function RotateHint() {
  const [dismissed, setDismissed] = useState(readDismissed)
  if (dismissed) return null

  const dismiss = () => {
    try {
      sessionStorage.setItem(STORAGE_KEY, '1')
    } catch {
      // non-essential; dismissal still applies for this page view
    }
    setDismissed(true)
  }

  return (
    <div className="rotate-hint" role="dialog" aria-modal="true" aria-labelledby="rotate-hint-title">
      <div className="rotate-hint-card">
        <span className="rotate-hint-icon" aria-hidden="true">
          ⟳
        </span>
        <h2 id="rotate-hint-title" className="mc-heading">
          TURN YOUR PHONE SIDEWAYS
        </h2>
        <p>The draft board needs the extra width. It's much easier to use in landscape.</p>
        <button className="mc-btn" onClick={dismiss}>
          CONTINUE ANYWAY
        </button>
      </div>
    </div>
  )
}
