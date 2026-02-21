const request = require('supertest');
const app = require('./server');

test('Health check should return OK', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('OK');
});

test('Should register student with valid data', async () => {
    const student = {
        name: 'John Doe',
        email: 'john@test.com',
        age: 22,
        course: 'CS'
    };
    
    const res = await request(app).post('/register').send(student);
    expect(res.statusCode).toBe(200);
    expect(res.body.success).toBe(true);
});

test('Should reject incomplete data', async () => {
    const incomplete = { name: 'Jane' };
    const res = await request(app).post('/register').send(incomplete);
    expect(res.statusCode).toBe(400);
    expect(res.body.success).toBe(false);
});
