number_of_days=7

function prepare_data(slug){
	console.log(slug)
        running_mean[slug] = running_mean[slug].slice(Math.max(running_mean[slug].length - number_of_days, 1))
        running_mean[slug].push((sessions[slug][6] + running_mean[slug][6]) / 2) //to give some idea of where we go from here...
        sessions[slug] = sessions[slug].slice(Math.max(sessions[slug].length - number_of_days, 1))
}

function get_dic(slug, color){
return  { type: 'bar', label: slug, backgroundColor: color, data: sessions[slug] }
}

prepare_data("EQT")
prepare_data("RHUL")
prepare_data("untagged")
prepare_data("PlanningAndTracking")
prepare_data("Email")

sum=[]
//for(var i = 0; i < running_mean["Family"].length; i++){
//   sum.push(running_mean["EQT"][i]+running_mean["Family"]);
//}

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday"]
        var d = new Date()
	daylabels=[]	
	for (i=-number_of_days;i<0;i++)
	{
		daylabels.push(weekdays[(d.getDay()+i+4900) % 7 ])//4900 is just a sufficiently large number that has 7 as a factor
	}

        var barChartData = {
            labels: daylabels,
            datasets: [
                 get_dic('PersonalProject',"rgba(0,0,24,0.35)") ,
                 get_dic('Family',"rgba(0,0,104,0.65)") ,
                 get_dic('EQT',"rgba(0,200,4,0.65)") ,
                 get_dic('Email',"rgba(200,0,4,0.65)") ,
                 get_dic('Exercise',"rgba(100,100,4,0.65)") ,
                 get_dic('RHUL',"rgba(100,100,100,0.65)") ,
                 get_dic('PlanningAndTracking',"rgba(0,100,200,0.65)") ,
                 get_dic('untagged',"rgba(250,250,250,0.65)") ,
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
                            barPercentage: 0.6
                        }]
                    }
                }
            });

        };
