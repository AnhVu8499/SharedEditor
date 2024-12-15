import React, { useState } from "react";
import { useRemirrorContext } from "@remirror/react";
import "./MenuBar.css";

const MenuBar = () => {
  const { commands } = useRemirrorContext();
  const [fontSize, setFontSize] = useState<string>("16px");
  const [textColor, setTextColor] = useState<string>("black");

  const handleTextColorChange = (color: string) => {
    setTextColor(color);
    commands.setTextColor(color); // Apply the text color command
  };

  return (
    <div className="menu-bar">
      {/* Bold */}
      <button onClick={() => commands.toggleBold()} className="menu-button">
        Bold
      </button>

      {/* Italic */}
      <button onClick={() => commands.toggleItalic()} className="menu-button">
        Italic
      </button>

      {/* Underline */}
      <button onClick={() => commands.toggleUnderline()} className="menu-button">
        Underline
      </button>

      {/* Font Size */}
      <select
        value={fontSize}
        onChange={(e) => {
          const size = e.target.value;
          setFontSize(size);
          commands.setFontSize(size);
        }}
        className="menu-select"
      >
        <option value="12px">12px</option>
        <option value="16px">16px</option>
        <option value="20px">20px</option>
        <option value="24px">24px</option>
        <option value="28px">28px</option>
        <option value="32px">32px</option>
        <option value="36px">36px</option>
        <option value="40px">40px</option>
      </select>

      {/* Text Color */}
      <select
        value={textColor}
        onChange={(e) => handleTextColorChange(e.target.value)}
        className="menu-select"
      >
        <option value="black">Black</option>
        <option value="red">Red</option>
        <option value="blue">Blue</option>
        <option value="green">Green</option>
      </select>
    </div>
  );
};

export default MenuBar;
