import React from 'react';
import { ContactForm } from './Components/contactform';
import { Form } from 'antd';

const ContactForms = Form.create({ name: 'register' })(ContactForm);

class App extends React.Component {
   render() {
      return (
         <div>
            <p>Lets See if This Works! This is being rendered from app.js</p>
            <ContactForm />
         </div>
      );
   }
}
export default App;