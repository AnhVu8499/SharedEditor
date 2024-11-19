import React, { useState, useEffect, useRef } from 'react';

const EditorComponent = ({ username }) => {
  const [isTyping, setIsTyping] = useState(false);
  const [content, setContent] = useState('');
  const [currentTyping, setCurrentTyping] = useState('');
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
      websocketRef.current.send(JSON.stringify({ 
        action: 'edit',
        username: username,
        content: newContent ,
      }));
    }
  };

  return (
    <div>
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
  );
};

export default EditorComponent;
