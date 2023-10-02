import json



# Parse the JSON data
data = json.load(open('verbose_institutions.json'))

# Extract the required information
extracted_data = []
for key, value in data.items():
    if 'Group' in key: continue
    try:


        entry = {
            "established": value["establish"],
            "name": value["name"],
            "lng_lat": [value["addresses"][0]["lng"], value["addresses"][0]["lat"]],
            "link": value["links"][0] if len(value["links"]) > 0 else None
        }
        extracted_data.append(entry)
    except:...

# Print the extracted data
# for entry in extracted_data:
#     print(entry)

mix = json.dumps(extracted_data)
print(mix)



plthtml= '''
<!DOCTYPE html>
<html>
<head>
    <title>World Map</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Include D3.js library -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/topojson@3"></script>
    <style>
        svg {
            width: 100vw;
            height: 100vh;
            top: 0;
            left: 0;
        }
    </style>
</head>
<body>
    <svg id="map"></svg>

    <script>
        // Create a SVG element for the map
        var svg = d3.select("#map");

        // Define the projection for the map
        var projection = d3.geoMercator()
            .center([0, 0])
            .translate([svg.node().clientWidth / 2, svg.node().clientHeight / 2*1.2])
            .scale(180)
            .center([0, 0])

        // Create a path generator
        var path = d3.geoPath()
            .projection(projection);

        // Load the world map data in TopoJSON format
        d3.json("https://unpkg.com/world-atlas/countries-50m.json").then(function (data) {
            // Convert TopoJSON to GeoJSON
            var countries = topojson.feature(data, data.objects.countries);

            // Draw the world map
            svg.selectAll("path")
                .data(countries.features)
                .enter().append("path")
                .attr("d", path)
                .attr("fill", "lightgray")
                .attr("stroke", "white");

            // Array of latitude and longitude points
            var points = '''+mix+''';

      
            // Scale for the established dates
            var establishedScale = d3.scaleLinear()
                .domain([d3.max(points, function(d) { return d.established; }),1])
                // .range([2, 8]); // Adjust the range as needed


            // Plot the points on the map
            svg.selectAll(".point")
                .data(points)
                .enter().append("circle")
                .attr("class", "point")
                .attr("cx", function (d) { return projection(d.lng_lat)[0]; })
                .attr("cy", function (d) { return projection(d.lng_lat)[1]; })
                .attr("r", function(d) { return 2 + 5*establishedScale(d.established||2022) })
                .attr("fill", "steelblue")
                .on("mouseover", function(e) {
                    var d = e.srcElement.__data__
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr("r",  6 + 15*establishedScale(d.established||2022)) // Increase the size
                        .attr("fill", "coral") // Change the color
                        .attr("opacity", 0.8) // Adjust the opacity if desired
                        .attr("stroke", "white"); // Add a stroke if desired
                })
                .on("mouseout", function(e) {
                    console.log(e,e.srcElement.__data__)
                    var d = e.srcElement.__data__
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr("r", 2 + 5*establishedScale(d.established||2022)) // Revert to the original size
                        .attr("fill", "steelblue") // Revert to the original color
                        .attr("opacity", 1) // Revert to the original opacity
                        .attr("stroke", null); // Remove the stroke
                })
                .on("click", function(d) {
                console.log(d.srcElement.__data__)
                    if (d.srcElement.__data__.link) {
                        window.open(d.srcElement.__data__.link, "_blank"); // Open the link in a new window/tab
                    }
                })
                .attr("title", function(d) { return d.name; }) // Set the tooltip text using the 'title' attribute
                .append("svg:title") // Required for some browsers to display the tooltip
                .text(function(d) { return d.name; })
                
        });
    </script>
</body>
</html>

'''

with open('institutions.html','w') as f:
    f.write(plthtml)