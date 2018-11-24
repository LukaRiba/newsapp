// const sum = require('../create_comment');
import * as fn from '../create_comment.js'


test('adds 1 + 2 to equal 3', () => {
  expect(fn.sum(1, 2)).toBe(3);
});