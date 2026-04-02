const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const { ServiceBuilder } = require('selenium-webdriver/chrome');

const BASE_URL = 'http://localhost:3000';
let driver;

beforeAll(async () => {
  const service = new ServiceBuilder(require('chromedriver').path);

  const options = new chrome.Options()
    .addArguments( '--no-sandbox', '--disable-dev-shm-usage')
    .setChromeBinaryPath('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe');

  driver = await new Builder()
    .forBrowser('chrome')
    .setChromeOptions(options)
    .setChromeService(service)
    .build();
}, 60000);

afterAll(async () => { if (driver) await driver.quit(); });

const fill = (id, val) => driver.findElement(By.id(id)).then(el => el.clear().then(() => el.sendKeys(val)));
const msg  = () => driver.wait(until.elementTextMatches(driver.findElement(By.id('msg')), /.+/), 5000).then(el => el.getText());
const removeRequired = () => driver.executeScript(`document.querySelectorAll('[required]').forEach(e => e.removeAttribute('required'))`);

async function fillForm(name, email, age, course) {
  await driver.get(BASE_URL);
  await fill('name', name);
  await fill('email', email);
  await fill('age', age);
  await driver.findElement(By.css(`#course option[value="${course}"]`)).click();
}

test('Page loads with title and form', async () => {
  await driver.get(BASE_URL);
  expect(await driver.getTitle()).toBe('Student Registration');
  expect(await driver.findElement(By.id('form')).isDisplayed()).toBe(true);
});

test('All form fields are present', async () => {
  for (const id of ['name', 'email', 'age', 'course']) {
    expect(await driver.findElement(By.id(id)).isDisplayed()).toBe(true);
  }
});

test('Successful registration clears form', async () => {
  await fillForm('James', `j_${Date.now()}@test.com`, '22', 'CS');
  await driver.findElement(By.css('button[type="submit"]')).click();
  expect(await msg()).toContain('successful');
  expect(await driver.findElement(By.id('name')).getAttribute('value')).toBe('');
});

test('Rejects missing fields', async () => {
  await driver.get(BASE_URL);
  await removeRequired();
  await driver.findElement(By.css('button[type="submit"]')).click();
  expect(await msg()).toMatch(/required/i);
});

test('Rejects age under 16', async () => {
  await fillForm('Bob', `b_${Date.now()}@test.com`, '12', 'WD');
  await removeRequired();
  await driver.findElement(By.css('button[type="submit"]')).click();
  expect(await msg()).toContain('16');
});

test('Rejects duplicate email', async () => {
  const email = `dup_${Date.now()}@test.com`;
  await fillForm('Carol', email, '25', 'DS');
  await driver.findElement(By.css('button[type="submit"]')).click();
  await msg();
  await fillForm('Carol2', email, '26', 'CS');
  await driver.findElement(By.css('button[type="submit"]')).click();
  expect(await msg()).toMatch(/already registered/i);
});

test('Health endpoint returns OK', async () => {
  await driver.get(`${BASE_URL}/health`);
  const body = JSON.parse(await driver.findElement(By.css('body')).getText());
  expect(body.status).toBe('OK');
});