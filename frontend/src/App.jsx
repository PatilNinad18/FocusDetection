import Background from "./components/Background";
import Navbar from "./components/Navbar";
import TimerCircle from "./components/TimerCircle";

export default function App() {
  return (
    <div className="relative w-screen h-screen">
      <Navbar/>
      <Background />
      <div className="absolute inset-0 bg-black/50"></div> {/* overlay */}
      <div className="absolute inset-0 flex items-center justify-center text-white">
        <TimerCircle/>
      </div>
    </div>

  );
}
