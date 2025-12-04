import "./Particles.css";

const Particles = () => {
  return (
    <div className="particles">
      {[...Array(10)].map((_, i) => (
        <div key={i} className="particle"></div>
      ))}
    </div>
  );
};

export default Particles;
