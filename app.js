// App.js
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/consent_db'
// App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CreateForm from './CreateForm';

const App = () => {
    const [forms, setForms] = useState([]);
    const [language, setLanguage] = useState('en');

    useEffect(() => {
        axios.get('/consent_forms', {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }).then(response => setForms(response.data));
    }, []);

    const handleLanguageChange = (e) => {
        setLanguage(e.target.value);
    };

    return (
        <div>
            <h1>Consent Form System</h1>
            <select value={language} onChange={handleLanguageChange}>
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
            </select>
            <CreateForm />
            <div>
                {forms.map(form => (
                    <div key={form.id}>
                        <h2>{form.patient_name}</h2>
                        <p>{form.consent_text}</p>
                        <p>{form.language}</p>
                        <p>{form.status}</p>
                        <p>{new Date(form.expiry_date).toLocaleDateString()}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default App;