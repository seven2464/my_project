// 模块1
(function() {
  var myChart = echarts.init(document.querySelector(".bar .chart"));
  var option = {
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b}: {c} ({d}%)"
    },
    legend: {
      orient: "vertical",
      left: 10,
      textStyle: { // 修改字体颜色和样式
        color: "#fff",
        fontSize: 14,
        fontStyle: "normal",
        fontWeight: "normal"
      },
      data: ["缺失", "溢胶", "油污", "孔洞","划痕"]
    },
    series: [
      {
        name: "缺陷数量",
        type: "pie",
        radius: "55%",
        center: ["50%", "60%"],
        data: [
          { value: 0, name: "缺失" },
          { value: 0, name: "溢胶" },
          { value: 0, name: "油污" },
          { value: 0, name: "孔洞" },
          { value: 0, name: "划痕" }
        ],
        label: {  // 设置标签为不显示
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)"
          },
        }
      }
    ]
  };
  myChart.setOption(option);
  window.addEventListener("resize", function() {
    myChart.resize();
  });

  // 获取数据并更新图表
  function getDataAndRefreshChart() {
    $.ajax({
      url: "/data",
      method: "GET",
      success: function(response) {
        console.log(response);
        option.series[0].data = [
          { value: response.defect_count_num_chipping, name: "缺失" },
          { value: response.defect_count_num_glueOverflow, name: "溢胶" },
          { value: response.defect_count_num_greasyDirt, name: "油污" },
          { value: response.defect_count_num_potholes, name: "孔洞" },
          { value: response.defect_count_num_scratches, name: "划痕" }
        ];
        myChart.setOption(option);
      },
      error: function(error) {
        console.log(error);
      }
    });
  }

  // 初始获取数据并刷新图表
  getDataAndRefreshChart();

})();

// 模块2
// 模块2
(function() {
  var myChart = echarts.init(document.querySelector(".line .chart"));

  // 发送 AJAX 请求获取 Flask 返回的数据
  $.ajax({
    url: "/accuracy_data",
    method: "GET",
    success: function(response) {
      // 找到最长的数据列表的长度
      var maxLength = Math.max(
        response.chipping.length,
        response.glueOverflow.length,
        response.greasyDirt.length,
        response.potholes.length,
        response.scratches.length
      );

      var xAxisData = [];
      for (var i = 0; i < maxLength; i++) {
        xAxisData.push((i + 1) + '%');
      }

      var option = {
        color: ["#4c9bfd", "green", "yellow"],
        tooltip: {
          trigger: "axis",
          formatter: "{b}<br/>{a}: {c}%" // 移除小数保留部分
        },
        legend: {
          right: "10%",
          textStyle: {
            color: "#4c9bfd"
          }
        },
        grid: {
          top: "20%",
          left: "3%",
          right: "4%",
          bottom: "3%",
          show: true,
          borderColor: "#012f4a",
          containLabel: true
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: xAxisData,
          axisTick: {
            show: false
          },
          axisLabel: {
            color: "rgba(255,255,255,.7)"
          },
          axisLine: {
            show: false
          }
        },
        yAxis: {
          type: "value",
          max:1, // 设置最大值为1
          axisTick: {
            show: false
          },
          axisLabel: {
            color: "rgba(255,255,255,.7)"
          },
          splitLine: {
            lineStyle: {
              color: "#012f4a"
            }
          },
          axisLabel: {
            formatter: "{value}%" // Y 轴标签格式化为百分比
          }
        },
        series: [
          {
            name: "缺失",
            type: "line",
            smooth: true,
            data: response.chipping.map(function(value) {
              return value || null;
            })
          },
          {
            name: "溢胶",
            type: "line",
            smooth: true,
            data: response.glueOverflow.map(function(value) {
              return value || null;
            })
          },
          {
            name: "油污",
            type: "line",
            smooth: true,
            data: response.greasyDirt.map(function(value) {
              return value || null;
            })
          },
          {
            name: "孔洞",
            type: "line",
            smooth: true,
            data: response.potholes.map(function(value) {
              return value || null;
            })
          },
          {
            name: "划痕",
            type: "line",
            smooth: true,
            data: response.scratches.map(function(value) {
              return value || null;
            })
          }
        ]
      };

      myChart.setOption(option);
      window.addEventListener("resize", function() {
        myChart.resize();
      });
    },
    error: function(error) {
      console.log(error);
    }
  });
})();


// (function() {
//   var myChart = echarts.init(document.querySelector(".line .chart"));
//   var data = {
//     year: [
//       [10,100,100,10,100,100,100,100,100,100],
//       [100,100,10,100,100,100,100,100,100,10],
//       [100,10,100,100,10,100,100,100,100,100],
//       [100,100,100,10,100,100,100,100,10,100],
//       [100,10,100,100,100,10,100,100,100,100]
//     ]
//   };
//   var option = {
//     color: ["#4c9bfd", "green","yellow"],
//     tooltip: {
//       trigger: "axis"
//     },
//     legend: {
//       right: "10%",
//       textStyle: {
//         color: "#4c9bfd"
//       }
//     },
//     grid: {
//       top: "20%",
//       left: "3%",
//       right: "4%",
//       bottom: "3%",
//       show: true,
//       borderColor: "#012f4a",
//       containLabel: true
//     },
//
//     xAxis: {
//       type: "category",
//       boundaryGap: false,
//       data: [
//         "10%",
//         "20%",
//         "30%",
//         "40%",
//         "50%",
//         "60%",
//         "70%",
//         "80%",
//         "90%",
//         "100%"
//       ],
//       axisTick: {
//         show: false
//       },
//       axisLabel: {
//         color: "rgba(255,255,255,.7)"
//       },
//       axisLine: {
//         show: false
//       }
//     },
//     yAxis: {
//       type: "value",
//       axisTick: {
//         show: false
//       },
//       axisLabel: {
//         color: "rgba(255,255,255,.7)"
//       },
//       splitLine: {
//         lineStyle: {
//           color: "#012f4a"
//         }
//       }
//     },
//     series: [
//       {
//         name: "缺失",
//         type: "line",
//         smooth: true,
//         data: data.year[0]
//       },
//       {
//         name: "溢胶",
//         type: "line",
//         smooth: true,
//         data: data.year[1]
//       },
//       {name: "油污",
//       type: "line",
//       smooth: true,
//       data: data.year[2]},
//         {
//         name: "孔洞",
//         type: "line",
//         smooth: true,
//         data: data.year[3]
//       },
//         {
//         name: "划痕",
//         type: "line",
//         smooth: true,
//         data: data.year[4]
//       }
//     ]
//   };
//   myChart.setOption(option);
//   myChart.setOption(option);
//   window.addEventListener("resize", function() {
//     myChart.resize();
//   });
// })();

//模块3
document.addEventListener("DOMContentLoaded", function() {
  var myChart = echarts.init(document.querySelector(".pie .chart"));

  function getDetectionTimeAndRefreshChart() {
    $.ajax({
      url: "/detection_time",
      method: "GET",
      success: function(response) {
        var option = {
          grid: {
            top: "10%",
            left: "9%",
            bottom: "10%",
            right: "3%"
          },
          xAxis: {
            type: 'category',
            data: response.detection_time_all.map((time, index) => index + 1)
          },
          yAxis: {
            type: 'value',
            min: 0, // 设置最小值为0
            max: 0.2 // 设置最大值为0.2
          },
          series: [{
            color: "yellow",
            symbolSize: 5,
            data: response.detection_time_all.map((time, index) => [index + 1, time]),
            type: 'scatter',
          }]
        };
        myChart.setOption(option);
      },
      error: function(error) {
        console.log("Error fetching detection times:", error);
      }
    });
  }

  getDetectionTimeAndRefreshChart();
  window.addEventListener("resize", function() {
    myChart.resize();
  });
});

// 模块4
(function() {
  var myChart = echarts.init(document.querySelector(".bar1 .chart"));

  // 发送 AJAX 请求获取数据
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/abc_judgment", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var data = JSON.parse(xhr.responseText);
      // 更新图表数据
      updateChart(data);
    }
  };
  xhr.send();

  function updateChart(data) {
    var option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          data: ['A级板', 'B级板', 'C级板'],
          axisTick: {
            alignWithLabel: true
          }
        }
      ],
      yAxis: [
        {
          type: 'value'
        }
      ],
      series: [
        {
          name: 'Direct',
          type: 'bar',
          barWidth: '60%',
          data: [
            { value: data.A_level_count, itemStyle: { color: 'red' } },
            { value: data.B_level_count, itemStyle: { color: 'blue' } },
            { value: data.C_level_count, itemStyle: { color: 'green' } }
          ]
        }
      ]
    };

    myChart.setOption(option);
  }

  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();


// # 模块5
(function() {
  var myChart = echarts.init(document.querySelector(".line1 .chart"));

  function updateChart(data) {
    var option = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category'
      },
      yAxis: {
        type: 'value',
        minInterval: 0.1
      },
      series: [{
        name: '图片面积',
        type: 'line',
        data: data
      }]
    };

    myChart.setOption(option);
    window.addEventListener("resize", function() {
      myChart.resize();
    });
  }

  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var responseData = JSON.parse(xhr.responseText);
      updateChart(responseData.defects_area_all); // 确保这里是处理好的一维数组数据
    }
  };
  xhr.open("GET", "/defects_area", true);
  xhr.send();
})();


//模块6
(function() {
  var myChart = echarts.init(document.querySelector(".pie1 .chart"));

  // 发送 AJAX 请求获取数据
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/damage_level", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var data = JSON.parse(xhr.responseText);
      // 更新图表数据
      updateChart(data);
    }
  };
  xhr.send();

  function updateChart(data) {
    var option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c}%'
      },
      toolbox: {}, // 将toolbox设置为空对象，表示不显示
      legend: {
        data: ['轻微', '完好', '严重', '中度']
      },
      series: [
        {
          name: 'Funnel',
          type: 'funnel',
          left: '10%',
          top: 60,
          bottom: 60,
          width: '80%',
          min: 0,
          max: 100,
          minSize: '0%',
          maxSize: '100%',
          sort: 'descending',
          gap: 2,
          label: {
            show: true,
            position: 'inside'
          },
          labelLine: {
            length: 10,
            lineStyle: {
              width: 1,
              type: 'solid'
            }
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1
          },
          emphasis: {
            label: {
              fontSize: 20
            }
          },
          data: [
            { value: data.slight_count, name: '轻微' },
            { value: data.perfect_count, name: '完好' },
            { value: data.severe_count, name: '严重' },
            { value: data.medium_count, name: '中度' }
          ]
        }
      ]
    };
    myChart.setOption(option);
  }

  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();



//数据展示.
$(document).ready(function() {
  var dataType = "title_data"; // 设置为你的 Flask 路由名称
  var toggleButton = document.getElementById("toggleButton");

  function fetchData() {
    var url = "/" + dataType;
    $.ajax({
      url: url,
      method: "GET",
      success: function(response) {
        // 更新页面上的元素，展示 Flask 返回的数据
        $("#total-quantity").text(response.total_count);
        $("#displayed-quantity").text(response.level_A_count);
      },
      error: function(error) {
        console.log(error);
      }
    });
  }

  // 调用 fetchData 函数来获取数据并更新页面
  fetchData();
});

//刷新按钮
function refreshPage() {
  location.reload();
}