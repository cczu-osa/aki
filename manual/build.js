const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SCREENSHOTS_DIR = 'screenshots'

if (fs.existsSync(SCREENSHOTS_DIR)) {
    fs.readdirSync(SCREENSHOTS_DIR).forEach(
        filename => fs.unlinkSync(path.join(SCREENSHOTS_DIR, filename))
    );
} else {
    fs.mkdirSync('screenshots');
}

fs.readdirSync('.').forEach(filename => {
    if (filename.endsWith('.html')) {
        const basename = path.parse(filename).name;
        const fullpath = path.resolve('.', filename);
        const destpath = path.join(SCREENSHOTS_DIR, `${basename}.png`);
        console.log(`Screenshotting ${filename}`);
        execSync(`npx screenshoteer --w 800 --url "file:///${fullpath}" --file "${destpath}"`);
    }
});
