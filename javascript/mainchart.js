number_of_days=7
//email
//vision
//jurgen
//

function prepare_data(slug){
        running_mean[slug] = running_mean[slug].slice(Math.max(running_mean[slug].length - number_of_days, 1))
        running_mean[slug].push((sessions[slug][6] + running_mean[slug][6]) / 2) //to give some idea of where we go from here...
        sessions[slug] = sessions[slug].slice(Math.max(sessions[slug].length - number_of_days, 1))

}

prepare_data("EQT")
prepare_data("Family")
prepare_data("PersonalProject")
//
sum=[]
for(var i = 0; i < running_mean["EQT"].length; i++){
   sum.push(running_mean["EQT"][i]+running_mean["Family"]);
}

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday"]
        var d = new Date()
        var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

	daylabels=[]	
	for (i=-number_of_days;i<0;i++)
	{
		daylabels.push(weekdays[(d.getDay()+i+4900) % 7 ])//4900 is just a sufficiantly large number that has 7 as a factor
	}

        var barChartData = {
            labels: daylabels,

            datasets: [
	    {
                    type: 'bar',
                    label: 'EQT',
                    backgroundColor: "rgba(0,0,0,0.25)",
                    data: sessions["EQT"]
                }, 
                {
                    type: 'bar',
                    label: 'PersonalProjects',
                    backgroundColor: "rgba(0,0,24,0.35)",
                    data: sessions["PersonalProject"]
                },
                {
                    type: 'bar',
                    label: 'Family',
                    backgroundColor: "rgba(0,0,24,0.35)",
                    data: sessions["Family"]
                },
 {
                    type: 'line',
                    label: 'Rolling Average',
                    backgroundColor: "rgba(220,0,0,0.5)",
                    data: sum
                }
            ]

        };

        window.onload = function() {
            var ctx = document.getElementById("canvas").getContext("2d");
            window.myBar = new Chart(ctx, {
                type: 'bar',
                data: barChartData,
                options: {
                    // Elements options apply to all of the options unless overridden in a dataset
                    // In this case, we are setting the border of each bar to be 2px wide and green
                    elements: {
                        rectangle: {
                            borderWidth: 2,
                            borderColor: 'rgb(0,0,0)',
                            borderSkipped: 'bottom'
                        }
                    },
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Vision Logged Hours'
                    },
                    scales: {
                        yAxes: [{
                            position: "left",
				      stacked: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Hours'
                            },
                            ticks: {
                                stepSize: 60,
				callback: function(label, index, labels){ return label/60;}

                            }
                        }],
                        xAxes: [{
                            // Change here
stacked: true,
                            barPercentage: 0.1
                        }]
                    }
                }
            });

        };
