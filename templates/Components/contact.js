import React from 'react';
import { Card } from 'antd';
import { Button } from 'antd';
import 'antd/dist/antd.css';


export class Contact extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            name: props.name,
            email: props.email,
            phone: props.phone}
    }
    render() {
        return(
            <div>
                <Card title="Contact Name" style={{ width: 300 }}>
                    <p>E-mail: </p>
                    <p>Phone: </p>
                </Card>
                <Button>Edit Contact</Button>
                <Button type="danger">Delete Contact</Button>
            </div>
        )
    }
}