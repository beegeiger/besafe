import React from 'react';
import { Card } from 'antd';

export class Contact extends React.Component{
    render() {
        return(
            <Card title="Default size card" extra={<a href="#">More</a>} style={{ width: 300 }}>
            <p>Card content</p>
            <p>Card content</p>
            <p>Card content</p>
          </Card>
        )
    }
}