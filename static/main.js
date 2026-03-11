// Auth State
let authMode = 'login'; // login or register

function switchAuthTab(mode) {
    authMode = mode;
    document.getElementById('tab-login').classList.toggle('active', mode === 'login');
    document.getElementById('tab-register').classList.toggle('active', mode === 'register');
    document.getElementById('auth-submit-btn').textContent = mode === 'login' ? 'Log In' : 'Create Account';

    const isRegister = mode === 'register';
    document.getElementById('name-group').classList.toggle('hidden', !isRegister);
    document.getElementById('confirm-pwd-group').classList.toggle('hidden', !isRegister);

    // Toggle required attributes
    document.getElementById('full_name').required = isRegister;
    document.getElementById('confirm_password').required = isRegister;

    document.getElementById('auth-error').classList.add('hidden');
    document.getElementById('auth-success').classList.add('hidden');
}

async function handleAuth(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const full_name = document.getElementById('full_name').value;
    const confirm_password = document.getElementById('confirm_password').value;

    const btn = document.getElementById('auth-submit-btn');
    const errObj = document.getElementById('auth-error');
    const succObj = document.getElementById('auth-success');

    errObj.classList.add('hidden');
    succObj.classList.add('hidden');

    if (authMode === 'register' && password !== confirm_password) {
        errObj.textContent = "Passwords do not match";
        errObj.classList.remove('hidden');
        return;
    }

    btn.disabled = true;

    const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';

    const payload = authMode === 'login'
        ? { email, password }
        : { full_name, email, password, confirm_password };

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.message || 'Authentication failed');
        }

        if (authMode === 'login') {
            const params = new URLSearchParams(window.location.search);
            const route = params.get('route');
            window.location.href = route ? `/dashboard?route=${route}` : '/dashboard';
        } else {
            succObj.textContent = "Registration successful! You can now Log In.";
            succObj.classList.remove('hidden');
            switchAuthTab('login');
        }

    } catch (err) {
        errObj.textContent = err.message;
        errObj.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
}

// Planning & Dashboard Navigation
function showSection(sectionId) {
    const sections = ['welcome-section', 'planner-section', 'experience-section', 'experience-results-section', 'my-trips-section', 'results-section', 'loading-state'];
    sections.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.toggle('hidden', id !== sectionId);
        }
    });

    if (sectionId === 'planner-section') {
        resetGenerateBtn();
    }

    if (sectionId === 'my-trips-section') {
        loadMyTrips();
    }
}

async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}

let placeCount = 0;

function addNextPlace() {
    placeCount++;
    const container = document.getElementById('places-container');

    const placeHTML = `
        <div class="glass-card mockup-card place-card" id="place-node-${placeCount}" style="max-width: 100%; margin-bottom: 1.5rem; transform: none; box-shadow: none; border-left: 4px solid var(--brand-primary);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>Place ${placeCount}</h4>
                ${placeCount > 1 ? `<button type="button" class="btn btn-secondary" style="padding: 0.2rem 0.6rem; font-size: 0.8rem;" onclick="removePlace(${placeCount})">Remove</button>` : ''}
            </div>
            
            <div class="form-row mt-2">
                <div class="input-group">
                    <label>Place Name</label>
                    <input type="text" class="p-name" required placeholder="e.g. Tea Museum">
                </div>
                <div class="input-group">
                    <label>Place Rating (1-5)</label>
                    <input type="number" class="p-rating" required min="1" max="5" step="0.1" placeholder="4.5">
                </div>
                <div class="input-group">
                    <label>Entry Fee / Expense (₹)</label>
                    <input type="number" class="p-fee" required min="0" placeholder="200" value="0" oninput="calculateTotalExpense()">
                </div>
            </div>
            
            <div class="form-row mt-2">
                <div class="input-group" style="flex-basis: 100%;">
                    <label>Experience Review (Optional)</label>
                    <textarea class="p-review" placeholder="Tell the community about your visit... was it worth the fee?" style="width : 100%; min-height: 60px; padding: 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid var(--border-subtle); border-radius: 8px; color: var(--text-primary);"></textarea>
                </div>
            </div>

            ${placeCount > 1 ? `
            <div class="form-row" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle);">
                <div class="input-group">
                    <label>Travel Method from Previous</label>
                    <select class="p-transport">
                        <option value="bus">Bus</option>
                        <option value="car">Car/Taxi</option>
                        <option value="train">Train</option>
                        <option value="walking">Walking</option>
                        <option value="bike">Bike</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Distance (km)</label>
                    <input type="number" class="p-distance" min="0" step="0.1" placeholder="15">
                </div>
                <div class="input-group">
                    <label>Travel Cost (₹)</label>
                    <input type="number" class="p-tcost" min="0" placeholder="100" value="0" oninput="calculateTotalExpense()">
                </div>
                <div class="input-group">
                    <label>Travel Rating</label>
                    <input type="number" class="p-trating" min="1" max="5" step="0.1" placeholder="4">
                </div>
            </div>
            ` : ''}
        </div>
    `;

    container.insertAdjacentHTML('beforeend', placeHTML);
}

function removePlace(id) {
    const el = document.getElementById(`place-node-${id}`);
    if (el) {
        el.remove();
        calculateTotalExpense();
    }
}

function calculateTotalExpense() {
    let total = 0;

    // 1. Stay Price
    const stayPrice = parseFloat(document.getElementById('exp_stay_price').value) || 0;
    total += stayPrice;

    // 2. Places Entry Fees
    document.querySelectorAll('.p-fee').forEach(input => {
        total += parseFloat(input.value) || 0;
    });

    // 3. Travel Costs
    document.querySelectorAll('.p-tcost').forEach(input => {
        total += parseFloat(input.value) || 0;
    });

    document.getElementById('calc-expense-display').innerText = `₹${total}`;
    return total;
}

async function handleExperienceSubmit(e) {
    e.preventDefault();

    const btn = document.getElementById('exp-submit-btn');
    const oldText = btn.querySelector('.btn-text').innerText;
    const loader = document.getElementById('exp-loader');

    btn.disabled = true;
    btn.querySelector('.btn-text').classList.add('hidden');
    loader.classList.remove('hidden');

    // Build JSON Payload
    const payload = {
        destination: document.getElementById('exp_dest').value,
        trip_date: document.getElementById('exp_date').value,
        companion_type: document.getElementById('exp_companion').value,
        stay_name: document.getElementById('exp_stay_name').value,
        stay_price: parseFloat(document.getElementById('exp_stay_price').value) || 0,
        stay_rating: parseFloat(document.getElementById('exp_stay_rating').value) || null,
        total_expense: calculateTotalExpense(),
        places: []
    };

    document.querySelectorAll('.place-card').forEach(card => {
        const pObj = {
            place_name: card.querySelector('.p-name').value,
            place_rating: parseFloat(card.querySelector('.p-rating').value) || null,
            entry_fee: parseFloat(card.querySelector('.p-fee').value) || 0,
            travel_method: card.querySelector('.p-transport') ? card.querySelector('.p-transport').value : null,
            distance_from_prev: card.querySelector('.p-distance') ? parseFloat(card.querySelector('.p-distance').value) : null,
            travel_cost: card.querySelector('.p-tcost') ? parseFloat(card.querySelector('.p-tcost').value) : 0,
            travel_rating: card.querySelector('.p-trating') ? parseFloat(card.querySelector('.p-trating').value) : null,
            experience_review: card.querySelector('.p-review').value || ""
        };
        payload.places.push(pObj);
    });

    try {
        const res = await fetch('/api/experiences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.status === 401) {
            window.location.href = '/login';
            return;
        }

        if (!res.ok) throw new Error("Failed to save experience");

        // Parse Payload to view the generated map immediately 
        renderExperienceItinerary(payload);

        e.target.reset();
        document.getElementById('places-container').innerHTML = '';
        placeCount = 0;
        addNextPlace(); // Re-add the first empty node
        calculateTotalExpense();

    } catch (err) {
        alert("Error saving experience. Check Console.");
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

async function loadMyTrips() {
    const container = document.getElementById('past-trips-list');
    if (!container) return;

    container.innerHTML = '<div class="loading-state"><div class="loader-spinner" style="margin: 0 auto;"></div><p>Loading your journeys...</p></div>';

    try {
        const res = await fetch('/api/my-trips');
        if (res.status === 401) {
            window.location.href = '/login';
            return;
        }

        const trips = await res.json();
        container.innerHTML = '';

        if (trips.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; margin-top: 2rem;">No past trips found. Start by registering your first experience!</p>';
            return;
        }

        trips.forEach(trip => {
            const tripCard = document.createElement('div');
            tripCard.className = 'glass-card mockup-card mt-2';
            tripCard.style.cssText = 'padding: 1.5rem; transform: none; box-shadow: none; margin-bottom: 1.5rem;';

            const placesText = trip.places.map(p => p.place_name).join(' → ');

            tripCard.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin-bottom: 0.25rem;">${trip.destination}</h3>
                        <p style="font-size: 0.85rem; color: var(--text-secondary);">${trip.trip_date || 'No date set'} • ${trip.companion_type || 'Solo'}</p>
                    </div>
                    <div class="budget-badge" style="padding: 0.25rem 0.75rem;">
                        <span class="value" style="font-size: 1rem;">₹${trip.total_expense}</span>
                    </div>
                </div>
                <div style="padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                    <p style="font-size: 0.9rem; color: var(--text-primary); line-height: 1.4;">${placesText}</p>
                </div>
                <div style="margin-top: 1rem; display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-secondary);">
                    <span>${trip.places.length} Places Visited</span>
                    <span>Stay: ${trip.stay_name || 'N/A'}</span>
                </div>
            `;
            container.appendChild(tripCard);
        });

    } catch (err) {
        container.innerHTML = '<p style="color: var(--accent-red); text-align: center;">Failed to load your trips. Please try again.</p>';
        console.error(err);
    }
}

function renderExperienceItinerary(data) {
    showSection('experience-results-section');

    document.getElementById('exp-result-dest').innerText = `Destination: ${data.destination || 'Unknown'}`;
    document.getElementById('exp-result-cost').innerText = `₹${data.total_expense || 0}`;

    const timeline = document.getElementById('experience-timeline');
    timeline.innerHTML = '';

    let simulatedTime = new Date();
    simulatedTime.setHours(9, 0, 0, 0); // Start at 09:00 AM

    data.places.forEach((place, index) => {

        // 1. If it's not the first place, render the travel block connecting them
        if (index > 0 && place.travel_method) {
            const travelHTML = `
                <div class="route-line" style="height: auto; min-height: 40px; margin-top: 10px; margin-bottom: 10px;"></div>
                <div class="route-item" style="margin-left: 20px; margin-bottom: 20px;">
                    <div class="details" style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.9rem;">
                        <span style="color: var(--brand-primary); font-weight: 500;">Travel: ${place.travel_method.charAt(0).toUpperCase() + place.travel_method.slice(1)}</span>
                        ${place.distance_from_prev ? `<span>Distance: ${place.distance_from_prev} km</span>` : ''}
                        <span>Cost: ₹${place.travel_cost || 0}</span>
                    </div>
                </div>
            `;
            timeline.innerHTML += travelHTML;

            // Add roughly 2 hours for travel & sightseeing overhead to the clock for visual simulation
            simulatedTime.setHours(simulatedTime.getHours() + 2);
        }

        const timeString = simulatedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const isLastNode = (index === data.places.length - 1);

        // 2. Render the actual Place node
        const placeHTML = `
            <div class="route-item" style="margin-top: 10px;">
                <div class="node"></div>
                <div class="details">
                    <span class="time">${timeString}</span>
                    <span class="place">${place.place_name}</span>
                    <span class="rating" style="color: var(--accent-yellow);">Rating: ${place.place_rating || 'N/A'}/5</span>
                    <span class="rating">Entry Fee: ₹${place.entry_fee || 0}</span>
                    ${place.experience_review ? `<p style="font-size: 0.8rem; font-style: italic; color: var(--text-secondary); margin-top: 0.5rem;">" ${place.experience_review} "</p>` : ''}
                </div>
            </div>
            ${!isLastNode ? '<div class="route-line"></div>' : ''}
        `;

        timeline.innerHTML += placeHTML;
    });
}

async function generateItinerary(e) {
    e.preventDefault();

    const dest = document.getElementById('destination').value;
    const budget = document.getElementById('budget').value;
    const duration = document.getElementById('duration').value;
    const transport = document.getElementById('transport').value;
    const style = document.getElementById('style').value;

    const submitBtn = document.getElementById('generate-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = document.getElementById('generate-loader');

    // UI State Start
    submitBtn.disabled = true;
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');

    showSection('loading-state');

    // Fake progress loading for UX purposes
    const loadingState = document.getElementById('loading-state');
    const listItems = loadingState.querySelectorAll('.loading-steps li');
    let delayCounter = 0;

    for (let i = 0; i < listItems.length; i++) {
        setTimeout(() => {
            listItems.forEach(el => el.classList.remove('active'));
            listItems[i].classList.add('active');
        }, delayCounter);
        delayCounter += 1000;
    }

    // API Call
    try {
        const res = await fetch('/api/generate-itinerary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                destination: dest,
                budget: Number(budget),
                duration: Number(duration),
                transport,
                style
            })
        });

        if (res.status === 401) {
            window.location.href = '/login';
            return;
        }

        const data = await res.json();

        // Let the UX loader finish its sequence before rendering
        setTimeout(() => {
            renderItinerary(data);
            // Render the Map
            if (data.days && data.days.length > 0) {
                renderMap(data);
            }
        }, delayCounter + 500);

    } catch (err) {
        alert("Failed to generate itinerary. Check console.");
        console.error(err);
        resetGenerateBtn();
        showSection('planner-section');
    }
}

// Global maps object mapping day numbers to Leaflet instances
let itineraryMaps = {};

async function renderMap(itineraryData) {
    const { destination, days, stay } = itineraryData;

    // Helper function for artificial delay
    const delay = ms => new Promise(res => setTimeout(res, ms));
    let isFirstReq = true;

    for (let dayIndex = 0; dayIndex < days.length; dayIndex++) {
        const day = days[dayIndex];
        const mapContainerId = `map-day-${day.day_number}`;
        const mapContainer = document.getElementById(mapContainerId);
        
        if (!mapContainer) continue;
        
        mapContainer.style.display = 'block';

        // Clean up pre-existing map instance for this day if re-generating
        if (itineraryMaps[day.day_number]) {
            itineraryMaps[day.day_number].off();
            itineraryMaps[day.day_number].remove();
        }

        itineraryMaps[day.day_number] = L.map(mapContainerId).setView([10.0, 76.0], 8);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(itineraryMaps[day.day_number]);

        const currentMap = itineraryMaps[day.day_number];

        const placesToGeocode = [];

        // Add Stay as the first origin point if it exists for Day 1
        if (day.day_number === 1 && stay && stay.name) {
            placesToGeocode.push({
                place: stay.name,
                time: 'Check-in',
                transport: 'stay'
            });
        }

        // Extract all places for this single day
        day.route.forEach(item => {
            if (item.place && item.place !== "Unknown") {
                placesToGeocode.push(item);
            }
        });

        if (placesToGeocode.length === 0) {
            mapContainer.style.display = 'none';
            continue;
        }

        mapContainer.style.opacity = '0.7';
        const coordinates = [];
        const markers = [];

        for (let i = 0; i < placesToGeocode.length; i++) {
            const item = placesToGeocode[i];
            try {
                // Respect Nominatim's 1 request/second policy across ALL geocodings
                if (!isFirstReq) await delay(1100);
                isFirstReq = false;
                
                const query = `${item.place}, ${destination}`;
                const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`, {
                    headers: {
                        'User-Agent': 'TravelItineraryApp/1.0 (LocalTest)'
                    }
                });
                const data = await response.json();

                if (data && data.length > 0) {
                    const lat = parseFloat(data[0].lat);
                    const lon = parseFloat(data[0].lon);
                    coordinates.push([lat, lon]);

                    const marker = L.marker([lat, lon]).addTo(currentMap);
                    const emoji = item.transport ? getTransportEmoji(item.transport) : '📍';
                    marker.bindPopup(`<b>${item.place}</b><br>Arrive: ${item.time} ${emoji}`);
                    markers.push(marker);
                } else {
                    console.warn(`Could not geocode location: ${query}`);
                }
            } catch (err) {
                console.error(`Geocoding failed for ${item.place}:`, err);
            }
        }

        mapContainer.style.opacity = '1.0';

        if (coordinates.length > 0) {
            const polyline = L.polyline(coordinates, {
                color: '#7B2CBF',
                weight: 3,
                opacity: 0.8,
                dashArray: '10, 10'
            }).addTo(currentMap);

            currentMap.fitBounds(polyline.getBounds(), { padding: [30, 30] });
            
            if (markers.length > 0) {
                markers[0].openPopup();
            }
        } else {
            // Hide map div completely if geocoding completely fails for this day
            mapContainer.style.display = 'none';
        }
    }
}

function renderItinerary(data) {
    showSection('results-section');
    resetGenerateBtn();

    document.getElementById('result-cost').textContent = `₹${data.total_cost || 0} `;

    const timeline = document.getElementById('itinerary-timeline');
    timeline.innerHTML = '';

    if (data.days && data.days.length > 0) {
        data.days.forEach(day => {
            // Add Day Header
            const dayHeader = `
                <div class="day-header" style="margin-top: 2rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-subtle);">
                    <h3 style="color: var(--brand-primary); display: flex; align-items: center; gap: 0.5rem;">
                        <span style="background: var(--brand-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">D</span>
                        Day ${day.day_number}
                    </h3>
                </div>
                <div id="map-day-${day.day_number}" style="height: 300px; width: 100%; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid var(--border-subtle); display: none;"></div>
            `;
            timeline.innerHTML += dayHeader;

            // Inject Stay at the beginning of Day 1
            if (day.day_number === 1 && data.stay && data.stay.name) {
                const stayHTML = `
                    <div class="route-item" style="margin-bottom: 2rem;">
                        <div class="node" style="background: var(--accent-yellow); box-shadow: 0 0 10px rgba(var(--accent-yellow-rgb), 0.5); border-color: rgba(var(--accent-yellow-rgb), 0.2);"></div>
                        <div class="details" style="background: rgba(var(--accent-yellow-rgb), 0.05); border: 1px solid rgba(var(--accent-yellow-rgb), 0.1);">
                            <div style="font-size: 0.8rem; color: var(--accent-yellow); text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 0.25rem;">Check-in</div>
                            <h3 class="place-name">${data.stay.name}</h3>
                            <div class="meta" style="margin-top: 0.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                                <span class="time">🏨 Accommodation</span>
                                <span class="rating" style="color: var(--accent-yellow);">⭐ ${data.stay.rating || 'N/A'}/5</span>
                                <span class="cost">₹${data.stay.price} total</span>
                            </div>
                        </div>
                    </div>
                `;
                timeline.innerHTML += stayHTML;
            }

            day.route.forEach((item, index) => {
                const isLast = (index === day.route.length - 1);

                const itemHTML = `
                    <div class="route-item">
                        <div class="node"></div>
                        <div class="details">
                            ${item.transport ? `
                                <div class="travel-bridge" style="
                                    background: rgba(var(--brand-primary-rgb), 0.05);
                                    border: 1px dashed rgba(var(--brand-primary-rgb), 0.2);
                                    border-radius: 8px;
                                    padding: 0.5rem 0.75rem;
                                    margin-bottom: 0.75rem;
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    font-size: 0.75rem;
                                ">
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span style="font-size: 1rem;">${getTransportEmoji(item.transport)}</span>
                                        <span style="font-weight: 600; color: var(--text-primary); text-transform: uppercase;">Via ${item.transport}</span>
                                        <span style="color: var(--text-secondary); margin-left: 0.25rem;">• ${item.distance || '0'} km</span>
                                    </div>
                                    <div style="font-weight: 700; color: var(--brand-primary);">Est. ₹${item.travel_cost || '0'}</div>
                                </div>
                            ` : ''}
                            <span class="time">${item.time}</span>
                            <span class="place">${item.place}</span>
                            <div class="metadata" style="display: flex; gap: 1rem; align-items: center; margin-top: 0.25rem;">
                                <span class="rating" style="color: var(--accent-yellow);">⭐ ${item.rating || 'N/A'}/5</span>
                                ${item.cost ? `<span class="cost">₹${item.cost}</span>` : ''}
                            </div>
                        ${item.reviews && item.reviews.length > 0 ? `
                        <div class="reviews-box" style="margin-top: 0.75rem; font-size: 0.85rem; color: var(--text-secondary); background: rgba(255,255,255,0.03); padding: 0.75rem; border-radius: 6px;">
                            <p style="font-weight: 500; margin-bottom: 0.25rem; color: var(--text-primary);">Community Reviews:</p>
                            <ul style="list-style: none; padding-left: 0;">
                                ${item.reviews.slice(0, 2).map(r => `<li style="margin-bottom: 0.25rem;">" ${r} "</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ${!isLast ? '<div class="route-line"></div>' : ''}
            `;
            timeline.innerHTML += itemHTML;
            });
        });
    }
}

function getTransportEmoji(method) {
    const m = method.toLowerCase();
    if (m.includes('car')) return '🚗';
    if (m.includes('bus')) return '🚌';
    if (m.includes('train')) return '🚆';
    if (m.includes('flight') || m.includes('plane')) return '✈️';
    if (m.includes('walk')) return '🚶';
    if (m.includes('bike') || m.includes('cycle')) return '🚲';
    if (m.includes('stay') || m.includes('hotel')) return '🏨';
    return '🗺️';
}

function resetGenerateBtn() {
    const submitBtn = document.getElementById('generate-btn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').classList.remove('hidden');
        document.getElementById('generate-loader').classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // If on the dashboard and looking for a specific route automatically
    const params = new URLSearchParams(window.location.search);
    const targetRoute = params.get('route');
    if (targetRoute === 'experience') {
        showSection('experience-section');
    }

    // Initialize first place card if container exists
    if (document.getElementById('places-container')) {
        addNextPlace();
    }
});
