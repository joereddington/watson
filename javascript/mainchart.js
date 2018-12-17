//refactoring :most of this should be in the individual javascript files
	number_of_days=7
//email
        emailrunning_mean = emailrunning_mean.slice(Math.max(emailrunning_mean.length - number_of_days, 1))
       emailrunning_mean.push((emailsessions[6] + emailrunning_mean[6]) / 2) //to give some idea of where we go from here...
      emailsessions = emailsessions.slice(Math.max(emailsessions.length - number_of_days, 1))
//vision
        projectsrunning_mean = projectsrunning_mean.slice(Math.max(projectsrunning_mean.length - number_of_days, 1))
        projectsrunning_mean.push((projectssessions[6] + projectsrunning_mean[6]) / 2) //to give some idea of where we go from here...
        projectssessions = projectssessions.slice(Math.max(projectssessions.length - number_of_days, 1))
//jurgen
        jurgenrunning_mean = jurgenrunning_mean.slice(Math.max(jurgenrunning_mean.length - number_of_days, 1))
        jurgensessions = jurgensessions.slice(Math.max(jurgensessions.length - number_of_days, 1))
        jurgenrunning_mean.push((jurgensessions[6] + jurgenrunning_mean[6]) / 2) //to give some idea of where we go from here...
//


        exerciserunning_mean = exerciserunning_mean.slice(Math.max(exerciserunning_mean.length - number_of_days, 1))
        exerciserunning_mean.push((exercisesessions[6] + exerciserunning_mean[6]) / 2) //to give some idea of where we go from here...
        exercisesessions = exercisesessions.slice(Math.max(exercisesessions.length - number_of_days, 1))
//
        journalsrunning_mean = journalsrunning_mean.slice(Math.max(journalsrunning_mean.length - number_of_days, 1))
        journalsrunning_mean.push((journalssessions[6] + journalsrunning_mean[6]) / 2) //to give some idea of where we go from here...
        journalssessions = journalssessions.slice(Math.max(journalssessions.length - number_of_days, 1))
//
sum=[]
//console.log("Jlength"+jurgenrunning_mean.length)
//console.log("Vlength"+running_mean.length)
for(var i = 0; i < journalsrunning_mean.length; i++){
	//console.log("V:"+running_mean[i]+" J:"+jurgenrunning_mean[i]);
   //sum.push(jurgenrunning_mean[i] + visionrunning_mean[i]+emailrunning_mean[i]);
   //sum.push(journalsrunning_mean[i]+jurgenrunning_mean[i]+projectsrunning_mean[i]);
   sum.push(journalsrunning_mean[i]+emailrunning_mean[i]+jurgenrunning_mean[i]+exerciserunning_mean[i]+projectsrunning_mean[i]);
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
                    label: 'Journaled time',
                    backgroundColor: "rgba(255, 165, 0,0.25)",
                    data: journalssessions
                }, 
                {
                    type: 'bar',
                    label: 'Exercise',
                    backgroundColor: "rgba(0,0,24,0.35)",
                    data: exercisesessions
                },
                {
                    type: 'bar',
                    label: 'Logged Next Actions Work',
                    backgroundColor: "rgba(0,0,240,0.35)",
                    data: jurgensessions
                },

                {
                    type: 'bar',
                    label: 'Logged Email Work',
                    backgroundColor: "rgba(240,0,0,0.25)",
                    data: emailsessions
                },   {
                    type: 'bar',
                    label: 'Logged Project Work',
                    backgroundColor: "rgba(240,240,0,0.25)",
                    data: projectssessions
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
