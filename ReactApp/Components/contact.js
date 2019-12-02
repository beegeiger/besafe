import React from 'react';
import { Card } from 'antd';
import { Button } from 'antd';

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
                <Card title={ this.state.name } extra={<a href="#">More</a>} style={{ width: 300 }}>
                    <p>E-mail: { this.state.email }</p>
                    <p>Phone: { this.state.phone }</p>
                </Card>
                <Button>Edit Contact</Button>
                <Button type="danger">Delete Contact</Button>
            </div>
        )
    }
}