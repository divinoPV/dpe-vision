<script>
    import {onMount} from 'svelte';

    let mapContainer;
    let map;
    let currentInfoWindow = null;

    function initMap() {
        const options = {
            center: {lat: 48.8587741, lng: 2.2069771},
            zoom: 10,
        };

        map = new google.maps.Map(mapContainer, options);
    }

    function getPolygonCenter(polygon) {
        let bounds = new google.maps.LatLngBounds();

        polygon.getPath().forEach((point) => {
            bounds.extend(point);
        });

        return bounds.getCenter();
    }

    async function fetchData() {
        try {
            const response = await fetch('http://localhost:8000/data');
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des données');
            }
            return await response.json(); // Convertir la réponse en JSON et la stocker dans la variable 'data'
        } catch (error) {
            console.error('Erreur:', error);
        }
    }

    async function showPolygonInfo(polygon, name_param, data) {
        if (currentInfoWindow) {
            currentInfoWindow.close();
        }

        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div>
                    <h3>${name_param}</h3>
                    <p>Traitement en cours...</p>
                </div>
            `,
        });

        currentInfoWindow = infoWindow;

        infoWindow.setPosition(getPolygonCenter(polygon));
        infoWindow.open(map);

        infoWindow.setContent(`
            <div>
                <h3>${name_param}</h3>
                ${data.sort((a, b) => (a["Etiquette_DPE"] > b["Etiquette_DPE"] ? 1 : -1)).map(d => `
                    <h5 style="margin-bottom: 3px;">
                        Il y a ${d["sum_dpe"]} étiqettes DPE de classe
                        ${d["Etiquette_DPE"]} pour les batiments de type ${d["Type_bâtiment"]}.
                    </h5>
                    <span>La surface moyenne habitable est de ${d["mean_surface_livable"] !== null ? parseFloat(d["mean_surface_livable"]).toFixed(2) : 0}.</span>
                    </br>
                    <span>La consommation moyenne de KWh est de ${d["mean_consumption_m2"] !== null ? parseFloat(d["mean_consumption_m2"]).toFixed(2) : 0}.</span>
                `)}
            </div>
        `);
    }


    async function fetchPolygons() {
        try {
            const response = await fetch('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson');
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des données');
            }
            return await response.json(); // Convertir la réponse en JSON et la retourner
        } catch (error) {
            console.error('Erreur:', error);
        }
    }

    function addMunicipalityPolygons(features, data) {
        features.forEach((feature) => {
            const currData = data.filter(d => feature.properties.code == d["Code_INSEE_(BAN)"]);
            const name_param = feature.properties.nom;
            const coordinates = feature.geometry.coordinates[0]; // Les coordonnées sont à l'index 0
            const polygonCoords = coordinates.map(coord => ({ lat: coord[1], lng: coord[0] })); // Inverser les coordonnées

            const polygon = new google.maps.Polygon({
                paths: polygonCoords,
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: '#FF0000',
                fillOpacity: 0.35,
            });

            polygon.setMap(map);

            google.maps.event.addListener(
                polygon,
                "click",
                () => showPolygonInfo(
                    polygon,
                    name_param,
                    currData,
                ),
            );
            return true;
        });
    }

    onMount(() => {
        if (typeof google !== 'undefined') initMap();
        fetchPolygons().then(polygons => fetchData().then(data => addMunicipalityPolygons(polygons.features, data)))
    });
</script>

<div class="map-container" bind:this={mapContainer}></div>

<style>
    .map-container {
        width: 100%;
        min-height: 98vh;
    }
    h5{
        margin: 0;
    }
</style>


