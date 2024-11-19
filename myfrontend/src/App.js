import React, { useState } from 'react';
import EditorComponent from './components/EditorComponent';
import Login from './components/Login';

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false); 
    const [username, setUsername] = useState(''); 

    const handleLogin = (loginStatus, username) => {
        setIsLoggedIn(loginStatus); 
        setUsername(username);
    };

    return (
        <div>
            {!isLoggedIn ? (
                <Login onLogin={handleLogin} />
            ) : (
                <>
                    <h1>Welcome, {username}!</h1>
                    <EditorComponent username={username} /> 
                </>
            )}
        </div>
    );
};

export default App;
