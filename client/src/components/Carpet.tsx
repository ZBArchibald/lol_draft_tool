// Static Sierpinski-carpet backdrop; the layers are styled in theme/background.css.
export default function Carpet() {
  return (
    <div className="carpet-wrap" aria-hidden="true">
      <div className="layer d1" />
      <div className="layer d2" />
      <div className="layer d3" />
      <div className="layer d4" />
      <div className="layer d5" />
    </div>
  )
}
