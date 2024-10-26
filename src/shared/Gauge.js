export function drawGauge(canvas, ctx, percentage, colour) {
    let startAngle  = -Math.PI / 2;
    let endAngle    = startAngle + (2 * Math.PI * percentage / 100);
    let radius      = 60;
    let lineWidth   = 20;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, radius, startAngle, 360);
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = "#fff3";
    ctx.lineCap = "round";
    ctx.stroke();
    ctx.closePath();

    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, radius, startAngle, endAngle);
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = colour;
    ctx.lineCap = "round";
    ctx.stroke();
    ctx.closePath();
    
    ctx.font = 'bold 45px WorkSans';
    ctx.fillStyle = colour;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(percentage, canvas.width / 2, canvas.height / 2);
}