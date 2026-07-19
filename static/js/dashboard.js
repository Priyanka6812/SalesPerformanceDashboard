document.addEventListener("DOMContentLoaded", function () {

    console.log("Analytics Dashboard Loaded");


    fetch("/chart-data")

        .then(response => response.json())

        .then(data => {


            // =========================
            // PRODUCT SALES CHART
            // =========================

            const productCanvas = document.getElementById("productChart");


            if (productCanvas) {

                new Chart(productCanvas, {

                    type: "bar",

                    data: {

                        labels: Object.keys(data.product),

                        datasets: [

                            {

                                label: "Product Sales",

                                data: Object.values(data.product)

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        plugins: {

                            legend: {

                                display: true

                            }

                        }

                    }

                });

            }




            // =========================
            // REGION SALES CHART
            // =========================

            const regionCanvas = document.getElementById("regionAnalysis");


            if (regionCanvas) {


                new Chart(regionCanvas, {

                    type: "pie",

                    data: {

                        labels: Object.keys(data.region),

                        datasets: [

                            {

                                label: "Region Sales",

                                data: Object.values(data.region)

                            }

                        ]

                    },


                    options: {

                        responsive: true

                    }

                });


            }





            // =========================
            // CATEGORY SALES CHART
            // =========================

            const categoryCanvas = document.getElementById("categoryChart");


            if (categoryCanvas) {


                new Chart(categoryCanvas, {


                    type: "doughnut",


                    data: {


                        labels: Object.keys(data.category),


                        datasets: [


                            {

                                label: "Category Sales",

                                data: Object.values(data.category)

                            }


                        ]


                    },


                    options: {

                        responsive: true

                    }


                });


            }



        })


        .catch(error => {


            console.log(
                "Chart Loading Error:",
                error
            );


        });


});