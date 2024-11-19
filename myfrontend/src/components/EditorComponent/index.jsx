import React, { useState, useEffect, useRef } from 'react';

const EditorComponent = ({ username }) => {
  const [isTyping, setIsTyping] = useState(false);
  const [content, setContent] = useState('');
  const [currentTyping, setCurrentTyping] = useState('');
  const [filename, setFilename] = useState('file');
  const websocketRef = useRef(null);  // WebSocket reference to persist across renders

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsTyping(false);
    }, 500);
    
    return () => clearTimeout(timeout);
  }, [content]);  // This runs every time 'content' changes


  useEffect(() => {
    // Open WebSocket connection based on the provided username
    websocketRef.current = new WebSocket(`ws://127.0.0.1:8000/ws/document/${username}`);

    websocketRef.current.onopen = () => {
      console.log(`WebSocket connection opened for document ${username}`);
    };

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setContent(data.content); 
      setCurrentTyping(data.username);
      setIsTyping(true);
    };

    websocketRef.current.onclose = () => {
      console.log(`WebSocket connection closed for document ${username}`);
    };

    // Clean up WebSocket on component unmount
    return () => {
      websocketRef.current.close();
    };
  }, [username]);  // Re-run this effect if the 'username' changes

  const handleInputChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    setIsTyping(true);
    setCurrentTyping(username);

    // Send updated content to the server via WebSocket
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      const data = JSON.stringify({
        action: 'edit',
        username: username,
        content: newContent
      });

      console.log(data);
      websocketRef.current.send(data);
    }
  };

  const handleFnameChange = (e) => {
    e.preventDefault();
    setFilename(e.target.value);
  }

  // When Save to File is clicked, downloads the contents of the editor into a new .txt file named after what the filename state is
  const handleExport = () => {
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const newName = filename + '.txt';
    link.setAttribute('download', newName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <div style={{display: 'flex', flexDirection: 'column', alignContent: 'center', justifyContent: 'center', width: '400px'}}>
        <input type="text" value={filename} onChange={handleFnameChange}/>
        <textarea
          id="editor"
          value={content}
          onChange={handleInputChange}
          placeholder="Start typing..."
          rows="10"
          cols="50"
        />
        {isTyping ? (
          <p> {currentTyping} is typing ... </p>
        ) : (
          <>
              <p>Waiting for input ...</p>
            </>
        )}
      </div>
      <button onClick={handleExport}>Save To File</button>

      
    </div>
  );
};

export default EditorComponent;
