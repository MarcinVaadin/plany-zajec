"use strict";
const Librus = require("librus-api");
const fs = require('fs');

const target_dir = 'calendars/synergia'

const args = process.argv.slice(2);
const data = fs.readFileSync(args[0])
const json = JSON.parse(data)

if (!fs.existsSync(target_dir)) {
    fs.mkdirSync(target_dir)
}

const metadata = new Array()

const client = new Librus();
json['synergia'].forEach(el => {
    const ics = target_dir + '/' + el.id + '.ics'
    metadata.push({
        'id': el.id,
        'ics': ics
    })
    client.authorize(process.env[el.user_env], process.env[el.pass_env]).then(function () {
        client._request("GET", "https://synergia.librus.pl/eksporty/ical/eksportuj/planUcznia").then((data) => 
            fs.writeFileSync(ics, data.text())
        )
    });
});
console.log(JSON.stringify(metadata))
