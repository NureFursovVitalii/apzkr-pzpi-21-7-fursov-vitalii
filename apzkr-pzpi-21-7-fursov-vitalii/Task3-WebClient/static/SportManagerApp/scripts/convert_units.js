var isImperial = false;

function toggleUnits() {
    var heightElement = document.getElementById("height");
    var weightElement = document.getElementById("weight");
    var heightUnitElement = document.getElementById("height-unit");
    var weightUnitElement = document.getElementById("weight-unit");
    var toggleButton = document.getElementById("toggleButton");

    if (isImperial) {
        var originalHeight = parseFloat(heightElement.getAttribute('data-original-height'));
        var originalWeight = parseFloat(weightElement.getAttribute('data-original-weight'));

        heightElement.innerText = originalHeight;
        weightElement.innerText = originalWeight;
        heightUnitElement.innerText = 'cm';
        weightUnitElement.innerText = 'kg';
        toggleButton.innerText = 'Toggle to Imperial Units';
    } else {
        var originalHeight = parseFloat(heightElement.innerText);
        var originalWeight = parseFloat(weightElement.innerText);

        var heightInInches = originalHeight / 2.54;
        var feet = Math.floor(heightInInches / 12);
        var inches = Math.round(heightInInches % 12);
        var weightInPounds = originalWeight * 2.20462;

        heightElement.innerText = `${feet} ft ${inches} in`;
        weightElement.innerText = weightInPounds.toFixed(2);
        heightUnitElement.innerText = '';
        weightUnitElement.innerText = 'lb';
        toggleButton.innerText = 'Toggle to Metric Units';
    }

    isImperial = !isImperial;
}
