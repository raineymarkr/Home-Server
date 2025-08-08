ho_oh_card_names = [
    "Tangela",
    "Tangrowth",
    "Hoppip",
    "Skiploom",
    "Jumpluff",
    "Heracross",
    "Slugma",
    "Magcargo",
    "Magby",
    "Entei",
    "Ho-oh ex",
    "Totodile",
    "Croconaw",
    "Feraligatr",
    "Marill",
    "Azumarill",
    "Delibird",
    "Ducklett",
    "Swanna",
    "Raikou",
    "Smoochum",
    "Togepi",
    "Togetic",
    "Togekiss",
    "Unown",
    "Girafarig",
    "Onix",
    "Gligar",
    "Gliscor",
    "Swinub",
    "Piloswine",
    "Mamoswine",
    "Phanpy",
    "Donphan ex",
    "Tyrogue",
    "Larvitar",
    "Pupitar",
    "Zubat",
    "Golbat",
    "Crobat ex",
    "Spinarak",
    "Ariados",
    "Umbreon ex",
    "Tyranitar",
    "Steelix",
    "Skarmory ex",
    "Klink",
    "Klang",
    "Klinklang",
    "Spearow",
    "Fearow",
    "Chansey",
    "Blissey",
    "Kangaskhan",
    "Sentret",
    "Furret",
    "Hoothoot",
    "Noctowl",
    "Teddiursa",
    "Ursaring",
    "Stantler",
    "Steel Apron",
    "Dark Pendant",
    "Silver",
    "Jasmine",
    "Hiker"
]

non_exclusive_card_names = [
    "Sunkern",
    "Sunflora",
    "Yanma",
    "Yanmega",
    "Pineco",
    "Cherubi",
    "Cherrim",
    "Darumaka",
    "Darmanitan",
    "Heatmor",
    "Emolga",
    "Jynx",
    "Snubbull",
    "Granbull",
    "Munna",
    "Musharna",
    "Sudowoodo",
    "Hitmontop",
    "Houndour",
    "Houndoom",
    "Absol",
    "Forretress",
    "Mawile",
    "Eevee",
    "Aipom",
    "Ambipom",
    "Dunsparce",
    "Bouffalant",
    "Rescue Scarf"
]

let cardList = {}

let cardNames = []

let tcgdex = null
let table

async function getSet(id) {
	try {
		const cards = await tcgdex.fetch('sets', id);
		return cards;
	} catch (e) {
		console.error(`Error fetching set ${id}`, e);
	}
}

async function getSavedSet(e) {
    const file = e.target.files[0];
    if (!file) return null;

    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = evt => {
            try {
                const json = JSON.parse(evt.target.result);
                resolve(json);
            } catch (err) {
                reject(err);
            }
        };
        reader.onerror = reject;
        reader.readAsText(file);
    });
}


async function login(username, password) {
    try{
        const response = await fetch('http://markrainey.me/login',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Login failed: ${errorData.message}`);
            }

            const data = await response.json();
            console.log('Login successful:', data);
            return data;
    } catch(error) {
        console.error('Error during login:', error);
        alert('Login failed. Please check your credentials.');
    }
}

function countCards(){
    let acquired_hooh = 0
    let acquired_lugia = 0
    let acquired_nonexclusive = 0
    let jsonlist = {}
    let unown = false

    for (let i  = 0; i < 160; i++){
        let cardName = cardNames[i]
        let checkbox = document.querySelector(`input[data-card-name="${cardName}"]`);
        if (checkbox && checkbox.checked) {
            if (ho_oh_card_names.includes(cardName) && cardName != 'Unown'){
                acquired_hooh += 1
            } else if (non_exclusive_card_names.includes(cardName)){
                acquired_nonexclusive += 1
            } else if (cardName == 'Unown'){
                if (unown == false){
                    acquired_hooh += 1
                    unown = true
                } else {
                    acquired_lugia += 1
                }
            } else {
                acquired_lugia += 1
            }
        }
        jsonlist[cardName] = checkbox.checked ? 1 : 0
    }
    
    console.log(jsonlist)
    console.log(`Ho-Oh Deck: ${acquired_hooh} cards, Lugia Deck: ${acquired_lugia} cards, Non-exclusive: ${acquired_nonexclusive} cards`)
}

async function loadFile(filePath){
    try{
        const response = await fetch(filePath);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading file:', error);
    }
}

function renderTable(saved = {}){
    tableBody = document.getElementById('card-table');
    tableBody.style.display = 'table-row-group';
    tableBody.replaceChildren();
    unown = false

    const frag = document.createDocumentFragment();
    for (let i = 0; i<= 160; i++){
        cardName = cardNames[i]
        const row = document.createElement('tr');

        const checkboxCell = document.createElement('td');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'card-checkbox';
        if (saved && saved[cardName]) checkbox.checked = true;
        checkbox.dataset.cardName = cardName;
        checkbox.dataset.cardDeck = cardList[cardName];
        checkboxCell.appendChild(checkbox);

        const nameCell = document.createElement('td');
        nameCell.className = 'card-name';
        nameCell.textContent = cardName;

        const deckCell = document.createElement('td');
        deckCell.className = 'card-deck';
        if(cardName != 'Unown'){
            deckCell.textContent = cardList[cardName];
        } else {
            if (!unown){
                deckCell.textContent = 'Ho-Oh';
                unown = true;
            } else {
                deckCell.textContent = 'Lugia';
            }
        }

        row.appendChild(checkboxCell);
        row.appendChild(nameCell);
        row.appendChild(deckCell);

        frag.appendChild(row);
    }

    tableBody.appendChild(frag);
}

window.onload = function() {
loggedin = false
saved = null
if(!loggedin){
    document.getElementById('loginModal').style.display = 'flex';
    document.getElementById('loginSubmit').onclick = async function() {
        const username = document.getElementById('modalUsername').value;
        const password = document.getElementById('modalPassword').value;
        loggedin = await login(username, password);
        if (loggedin) {
            document.getElementById('loginModal').style.display = 'none';
        }
    }
}
if (loggedin != false) {
    document.getElementById('loginModal').style.display = 'none';
    tcgdex = new TCGdex('en'); 
    //saved = loadFile('http://markrainey.me/datastore/savedJson.txt');
    getSet('Wisdom of Sea and Sky').then(cards => {
        if (cards) {
        for(let i = 0 ; i < cards.cards.length; i++){
            if(cards.cards[i].localId < 202){
            if (ho_oh_card_names.includes(cards.cards[i].name)){
                cardDeck = 'Ho-Oh'
            } else if (non_exclusive_card_names.includes(cards.cards[i].name)){
                cardDeck = 'Either'
            } else {
                cardDeck = 'Lugia'
            }
            cardList[cards.cards[i].name] = cardDeck
            cardNames.push(cards.cards[i].name)
            }
        }		
        }


        renderTable(saved);
        });

        
        document.getElementById('log-button').onclick = function() {
            const checkedCards = [];
            const checkboxes = document.getElementsByClassName('card-checkbox');
            for (const checkbox of checkboxes) {
                checkedCards.push({
                    name: checkbox.dataset.cardName,
                    deck: checkbox.dataset.cardDeck,
                    acquired: checkbox.checked
                });
            }
            countCards()
        }

        document.getElementById('file-input').addEventListener('change', async e => { 
            try {
                saved = await getSavedSet(e);
                renderTable(saved);
            } catch (err) {
                console.error('Error reading file:', err);
            }
        });
    }
 }


