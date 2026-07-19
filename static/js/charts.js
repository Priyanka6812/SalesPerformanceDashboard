document.addEventListener("DOMContentLoaded", function () {


fetch("/chart-data")

.then(response => response.json())

.then(data => {


    // Monthly/Product Sales Chart

    const salesCanvas = document.getElementById("salesChart");


    if(salesCanvas){

        new Chart(
            salesCanvas,
            {
                type: "line",

                data: {

                    labels: Object.keys(data.product),

                    datasets: [

                    {
                        label: "Product Sales",

                        data: Object.values(data.product),

                        borderWidth: 3,

                    }

                    ]

                },


                options: {

                    responsive:true,

                    scales: {

                        y: {

                            beginAtZero:true

                        }

                    }

                }

            }
        );

    }





    // Region Chart


    const regionCanvas = document.getElementById("regionChart");


    if(regionCanvas){


        new Chart(

            regionCanvas,

            {

                type:"doughnut",


                data:{


                    labels:Object.keys(data.region),


                    datasets:[

                    {

                    label:"Region Sales",

                    data:Object.values(data.region),

                    borderWidth:1

                    }

                    ]

                },


                options:{


                    responsive:true


                }


            }

        );


    }



})


.catch(error => {

console.log(
"Chart Error:",
error
)

});


});