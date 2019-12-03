import React from 'react';

import { ContactForm } from './Components/contactform';


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