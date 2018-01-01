//refactoring :most of this should be in the individual javascript files
	number_of_days=7
//email
        DELORESrunning_mean = DELORESrunning_mean.slice(Math.max(DELORESrunning_mean.length - number_of_days, 1))
       DELORESrunning_mean.push((DELORESsessions[6] + DELORESrunning_mean[6]) / 2) //to give some idea of where we go from here...
      DELORESsessions = DELORESsessions.slice(Math.max(DELORESsessions.length - number_of_days, 1))
//vision

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
                    label: 'Unlabeled Work',
                    backgroundColor: "rgba(0,0,0,0.25)",
                    data: DELORESsessions
                }, 

 {
                    type: 'line',
                    label: 'Rolling Average',
                    backgroundColor: "rgba(220,0,0,0.5)",
                    data: DELORESrunning_mean
                }
            ]

        };

        window.onload = function() {
            var ctx = document.getElementById("canvas2").getContext("2d");
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
