import React, { useState } from 'react';

const SignUp = ({ onSignUp }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();

        // POST request to backend signup endpoint
        const response = await fetch('http://127.0.0.1:8000/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            onSignUp(true, username, password);
            alert(`New user - ${username} has been created`);
        } else {
            alert('Invalid Username or password');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
            />
            <button type="submit">Sign Up</button>
        </form>
    );
};

export default SignUp;
