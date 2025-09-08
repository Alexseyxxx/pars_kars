GET_AREAS = """
const regions = [];

window.document.querySelectorAll('li.filter-region__item').forEach(li => {
    const btn = li.querySelector('button');
    const alias = btn.getAttribute('data-alias');
    const label = li.innerText;

    if (label) {
        regions.push({ alias, label });
    }
});
regions;
"""
GET_ADVERTS_IDS = """
const ids = [];

window.document.querySelectorAll(
'.a-card.js__a-card'
).forEach(advert => {
    const id = advert.getAttribute("data-id");
    if (id) {
        ids.push(id);
    }
})
ids;
"""
GET_ADVERTS_DATES = """
const dates = [];

window.document.querySelectorAll(
'div.a-card__info > div.a-card__footer > div.a-card__data > span.a-card__param.a-card__param--date'
).forEach(advert => {
    const date = advert.innerText;
    if (date) {
        dates.push(date);
    }
})
dates;
"""

GET_TITLE = """
let title = window.document.querySelector("[itemprop='brand'").innerText;
title;
"""
GET_DESCR = """
let descr = window.document.querySelector(".a-description__text").innerText;
descr;
"""
GET_YEAR = """
let year = window.document.querySelector("span.year").innerText;
year;
"""
GET_CHARS = """
const params = {};
document.querySelectorAll(".offer__parameters dl").forEach(dl => {
  const key = dl.querySelector("dt")?.innerText.trim().replace(/\u00a0/g, " ");
  const value = dl.querySelector("dd")?.innerText.trim();
  if (key && value) {
    params[key] = value;
  }
});
params;
"""
GET_PRICE = """
let price = window.document.querySelector(".offer__price").innerText;
price;
"""
GET_IMAGES = """
let urls = [];
window.document.querySelectorAll("button.gallery__thumb-image").forEach(element => {
    let photoUrl = element.getAttribute("data-href");
    urls.push(photoUrl);
});
urls;
"""