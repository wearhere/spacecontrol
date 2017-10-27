// HACK(jeff): This is to be applied to component DOM nodes, though it should probably be applied at
// the parent level, but that breaks this painstakingly-Stack Overflow-sourced CSS then. :p
// https://stackoverflow.com/a/11716065/495611
const vAlignImage = {
  position: 'absolute',
  top: 0,
  bottom: 0,
  margin: 'auto'
};

export default vAlignImage;
