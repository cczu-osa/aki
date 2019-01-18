// set html head
document.head.innerHTML = '<meta charset="utf-8"> \
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> \
    <link rel="stylesheet" href="css/style.css">';

// generate header
let functionName = '';
let h1 = document.querySelector('h1');
if (h1) {
    h1.remove();
    functionName = h1.innerText.trim();
}
let header = document.createElement('header');
header.innerHTML = `<span>奶茶使用帮助</span> \
    <span class="function-name">${functionName}</span>`;
document.body.prepend(header);

// move sections into main
let sections = document.querySelectorAll('section');
let main = document.createElement('main');
sections.forEach(s => {
    s.remove();
    main.append(s);
});
document.body.append(main);

// generate footer
let footer = document.createElement('footer');
footer.innerHTML = '<span>常州大学开源软件协会</span> \
    <img src="img/osa-logo.png" alt="" width="110px" height="110px">';
document.body.append(footer);
