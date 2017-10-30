import React from 'react';

export default function HUD(props) {
  return (
    <div className='hud'>
      <h2>{props.level}</h2>;
    </div>
  );
}
