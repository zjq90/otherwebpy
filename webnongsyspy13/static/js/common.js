/*
农产品溯源与认证管理系统
通用JavaScript工具函数
*/

/**
 * 显示消息提示模态框
 * @param {string} title - 标题
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, error, warning, info)
 */
function showMessage(title, message, type) {
    var $modal = $('#messageModal');
    var $title = $('#messageModalTitle');
    var $body = $('#messageModalBody');
    
    $title.text(title);
    $body.html(message);
    
    // 根据类型设置样式
    $title.removeClass('text-success text-danger text-warning text-info');
    switch(type) {
        case 'success':
            $title.addClass('text-success');
            break;
        case 'error':
            $title.addClass('text-danger');
            break;
        case 'warning':
            $title.addClass('text-warning');
            break;
        case 'info':
            $title.addClass('text-info');
            break;
    }
    
    $modal.modal('show');
}

/**
 * 显示确认对话框
 * @param {string} message - 确认消息
 * @param {function} onConfirm - 确认回调函数
 * @param {function} onCancel - 取消回调函数
 */
function confirmAction(message, onConfirm, onCancel) {
    if (confirm(message)) {
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    } else {
        if (typeof onCancel === 'function') {
            onCancel();
        }
    }
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期对象或日期字符串
 * @returns {string} 格式化后的日期字符串 (YYYY-MM-DD)
 */
function formatDate(date) {
    if (!date) return '';
    
    var d = new Date(date);
    var year = d.getFullYear();
    var month = String(d.getMonth() + 1).padStart(2, '0');
    var day = String(d.getDate()).padStart(2, '0');
    
    return year + '-' + month + '-' + day;
}

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期对象或日期字符串
 * @returns {string} 格式化后的日期时间字符串 (YYYY-MM-DD HH:mm:ss)
 */
function formatDateTime(date) {
    if (!date) return '';
    
    var d = new Date(date);
    var year = d.getFullYear();
    var month = String(d.getMonth() + 1).padStart(2, '0');
    var day = String(d.getDate()).padStart(2, '0');
    var hours = String(d.getHours()).padStart(2, '0');
    var minutes = String(d.getMinutes()).padStart(2, '0');
    var seconds = String(d.getSeconds()).padStart(2, '0');
    
    return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
}

/**
 * 获取状态标签HTML
 * @param {string} status - 状态值
 * @returns {string} Bootstrap徽章HTML
 */
function getStatusBadge(status) {
    var badgeClass = 'badge-secondary';
    var displayText = status;
    
    switch(status) {
        case '有效':
            badgeClass = 'badge-success';
            break;
        case '即将过期':
            badgeClass = 'badge-warning';
            break;
        case '过期':
            badgeClass = 'badge-danger';
            break;
        case '合格':
            badgeClass = 'badge-success';
            break;
        case '不合格':
            badgeClass = 'badge-danger';
            break;
        case '自检':
            badgeClass = 'badge-info';
            break;
        case '第三方检测':
            badgeClass = 'badge-primary';
            break;
    }
    
    return '<span class="badge ' + badgeClass + '">' + displayText + '</span>';
}

/**
 * 加载表格数据
 * @param {string} url - API地址
 * @param {string} tableSelector - 表格选择器
 * @param {function} renderRow - 渲染每行的回调函数
 */
function loadTableData(url, tableSelector, renderRow) {
    var $tableBody = $(tableSelector + ' tbody');
    $tableBody.html('<tr><td colspan="10" class="text-center"><span class="loading-spinner"></span> 加载中...</td></tr>');
    
    $.get(url)
        .done(function(data) {
            if (data && data.length > 0) {
                var html = '';
                data.forEach(function(item, index) {
                    html += renderRow(item, index);
                });
                $tableBody.html(html);
            } else {
                var colspan = $tableBody.closest('table').find('thead th').length;
                $tableBody.html(
                    '<tr><td colspan="' + colspan + '" class="text-center text-muted">' +
                    '<i class="fas fa-inbox mr-2"></i>暂无数据' +
                    '</td></tr>'
                );
            }
        })
        .fail(function(xhr) {
            var colspan = $tableBody.closest('table').find('thead th').length;
            var errorMsg = xhr.responseJSON && xhr.responseJSON.detail 
                ? xhr.responseJSON.detail 
                : '加载数据失败';
            $tableBody.html(
                '<tr><td colspan="' + colspan + '" class="text-center text-danger">' +
                '<i class="fas fa-exclamation-triangle mr-2"></i>' + errorMsg +
                '</td></tr>'
            );
        });
}

/**
 * 通过ID删除数据
 * @param {string} url - API地址
 * @param {number} id - 数据ID
 * @param {string} itemName - 项目名称（用于提示消息）
 * @param {function} onSuccess - 成功回调
 */
function deleteById(url, id, itemName, onSuccess) {
    confirmAction('确定要删除该' + itemName + '吗？此操作不可恢复。', function() {
        $.ajax({
            url: url + '/' + id,
            method: 'DELETE'
        })
        .done(function() {
            showMessage('成功', itemName + '删除成功！', 'success');
            if (typeof onSuccess === 'function') {
                onSuccess();
            }
        })
        .fail(function(xhr) {
            var errorMsg = xhr.responseJSON && xhr.responseJSON.detail 
                ? xhr.responseJSON.detail 
                : '删除失败';
            showMessage('错误', errorMsg, 'error');
        });
    });
}

/**
 * 表单数据序列化（支持嵌套对象）
 * @param {jQuery} $form - 表单jQuery对象
 * @returns {object} 序列化后的对象
 */
function serializeForm($form) {
    var formData = {};
    var array = $form.serializeArray();
    
    array.forEach(function(item) {
        var name = item.name;
        var value = item.value;
        
        // 处理日期类型
        if (name.includes('date') && value) {
            formData[name] = value;
        } 
        // 处理数字类型
        else if (['quantity', 'product_id', 'batch_id', 'safety_interval'].includes(name)) {
            formData[name] = value ? Number(value) : null;
        }
        // 处理空值
        else if (value === '') {
            formData[name] = null;
        }
        else {
            formData[name] = value;
        }
    });
    
    return formData;
}

/**
 * 填充表单数据
 * @param {jQuery} $form - 表单jQuery对象
 * @param {object} data - 数据对象
 */
function populateForm($form, data) {
    for (var key in data) {
        if (data.hasOwnProperty(key)) {
            var $input = $form.find('[name="' + key + '"]');
            if ($input.length > 0) {
                var value = data[key];
                // 处理日期类型
                if (value && (key.includes('date') || key.includes('Date'))) {
                    if (typeof value === 'string') {
                        value = value.split('T')[0];
                    }
                }
                $input.val(value);
            }
        }
    }
}

/**
 * 计算两个日期之间的天数
 * @param {string|Date} date1 - 日期1
 * @param {string|Date} date2 - 日期2
 * @returns {number} 天数差
 */
function daysBetween(date1, date2) {
    var d1 = new Date(date1);
    var d2 = new Date(date2);
    var diffTime = d2 - d1;
    var diffDays = diffTime / (1000 * 60 * 60 * 24);
    return Math.ceil(diffDays);
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 */
function copyToClipboard(text) {
    var $temp = $('<input>');
    $('body').append($temp);
    $temp.val(text).select();
    document.execCommand('copy');
    $temp.remove();
    showMessage('成功', '已复制到剪贴板：' + text, 'success');
}

// 页面加载完成后执行
$(document).ready(function() {
    // 初始化提示框
    $('[data-toggle="tooltip"]').tooltip();
    
    // 初始化弹出框
    $('[data-toggle="popover"]').popover();
    
    // 表单提交防重处理
    $('form').on('submit', function() {
        var $submitBtn = $(this).find('[type="submit"]');
        $submitBtn.prop('disabled', true);
        $submitBtn.html('<span class="loading-spinner mr-2"></span>处理中...');
    });
});
