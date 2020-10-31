function makeTable(data, tableId){
    //  表の作成開始
    var rows=[];
    var table = document.createElement("table");
    var msg = JSON.stringify(data);
    var t = JSON.parse(msg);
    var keys = Object.keys(t[0]);
    
    for(i = 0; i < 1; i++){
        rows.push(table.insertRow(-1));  // 行の追加
        for(j = 0; j <t.length; j++){
            cell=rows[i].insertCell(-1);
            cell.appendChild(document.createTextNode(keys[j]));
            cell.style.backgroundColor = "#bbb"; // ヘッダ行以外
        }
    }

    // 表に2次元配列の要素を格納
    for(i = 0; i < keys.length; i++){
        rows.push(table.insertRow(-1));  // 行の追加
        for(j = 0; j <t.length; j++){
            cell=rows[i].insertCell(-1);
            var key = keys[j];
            var value = t[i][key];
            cell.appendChild(document.createTextNode(value));
            cell.style.backgroundColor = "#ddd"; // ヘッダ行以外
        }
    }
    // 指定したdiv要素に表を加える
    document.getElementById(tableId).appendChild(table);
}
window.onload = function(){ 
// 表のデータ
var data = [
{ name : "taro", pref : "27", date : "1" },
{ name : "yuta", pref : "27", date : "3" },
{ name : "ziro", pref : "27", date : "12" }
];

// 表の動的作成
makeTable(data,"table");
};