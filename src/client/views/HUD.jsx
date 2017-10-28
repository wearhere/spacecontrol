import React from 'react';

export default function HUD(props) {
  return (
    <div className='hud'>
      <h1>{props.level}</h1>;
    </div>
  );
}
