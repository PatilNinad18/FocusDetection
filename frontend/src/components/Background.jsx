import React from "react";
import spaceBg from "../assets/banner2.jpg";

export default function Background() {
  const bg = {
    backgroundImage: `url(${spaceBg})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    height: "100vh",
    width: "100vw",
  };

  return <div style={bg}></div>;
}
