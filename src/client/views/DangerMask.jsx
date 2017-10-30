import React from 'react';

export default function DangerMask(props) {
  return <div className="danger-mask" data-state={props.fatal && 'fatal'} />;
}
