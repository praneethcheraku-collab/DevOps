// app1.test.js - Tests for app1.js

const {
    runDynamicCode,
    hashData,
    validateUser1,
    validateUser2,
    unusedParam,
    processData,
    complexLogic
} = require('./app1');

describe('app1.js - Enhanced sample tests', () => {

    test('runDynamicCode executes arithmetic', () => {
        expect(runDynamicCode('15 + 25')).toBe(40);
    });

    test('hashData returns a string', () => {
        const result = hashData('test');
        expect(typeof result).toBe('string');
        expect(result.length).toBeGreaterThan(0);
    });

    test('validateUser1 accepts valid-looking input', () => {
        expect(validateUser1('user@example.com')).toBe(true);
        expect(validateUser1(null)).toBe(false);
    });

    test('validateUser2 works identically', () => {
        expect(validateUser2('user@example.com')).toBe(true);
    });

    test('processData handles null and string', () => {
        expect(processData(null)).toBe(0);
        expect(processData('hello')).toBe(5);
    });

    test('complexLogic returns Normal for typical values', () => {
        expect(complexLogic(50)).toBe('Normal');
        expect(complexLogic(0)).toBe('Normal');
    });

    test('unusedParam function can be called', () => {
        // Mock console to avoid output noise
        const logSpy = jest.spyOn(console, 'log').mockImplementation();
        unusedParam('test value', 'ignored');
        expect(logSpy).toHaveBeenCalledWith('test value');
        logSpy.mockRestore();
    });
});