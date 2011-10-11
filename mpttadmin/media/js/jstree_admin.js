$(document).ready(function() {
    if (!$('#tree').length)
        return false;

    $(function() {
        window.jtree = $("#tree").tree({
            /*ui: {
                theme_name: 'apple'
            },*/

            plugins: {
                contextmenu: {
                    items: {
                        remove: true,
                        create: {
                            label: "Create",
                            icon: "create",
                            visible: function(node, treeobj) {
                                if (node.length != 1)
                                    return 0;
                                return treeobj.check("creatable", node);
                            },
                            action: function(node, treeobj) {
                                location.href = 'add/?'+parent_attr+'='+node.attr('id').replace('n','');
                                },
                            separator_after: true
                        },
                        rename: {
                            label: "Rename",
                            icon: "rename",
                            visible: function(node, treeobj) {
                                if (node.length != 1)
                                    return false;
                                return treeobj.check("renameable", node);
                            },
                            action: function(node, treeobj) {
                                treeobj.rename(node);
                            }
                        },
                        edit: {
                            label: "Change",
                            icon: "rename",
                            visible: function(node, treeobj) {
                                if (node.length != 1)
                                    return false;
                                return true;
                            },
                            action: function(node, treeobj) {
                                location.href = $(node).attr('id').replace('n','') + '/';
                            }
                        },
                        remove: {
                            label: "Remove",
                            icon: "remove",
                            visible: function(node, treeobj) {
                                if (node.length != 1)
                                    return false;
                                return treeobj.check("deletable", node);
                            },
                            action: function(node, treeobj) {

                                treeobj.remove(node);
                                
                            }
                        }

                    }
                }

            },

            callback: {
                beforemove: function(node, ref_node, TYPE, treeobj) {
                    if(treeobj._moving){
                        treeobj._moving=false;
                        return true;
                    }else treeobj._moving=true;
                    var position={'inside':'last-child','before':'left','after':'right'}[TYPE];
                    treeobj.settings.data.opts.url = 'move_node/';
                    treeobj.settings.data.opts.method='POST';
                    treeobj._params={node:node.id.replace('n',''),target:ref_node.id.replace('n',''),position:position};

                    treeobj.refresh();
                    return false;
                },
                ondblclk: function(node, treeobj) {
                    location.href = $(node).attr('id').replace('n','');
                },
                /*onload: function(treeobj) {
                    treeobj.open_all();
                },*/
                onrename: function(node, treeobj, RB) {
                    var new_name=$(node).children('a:first').text();//.replace(/^\s\s*/, '');
                    var par=treeobj.parent(node);
                    var id=(par==-1?0:par.attr('id').replace('n',''));
                    treeobj._params={node:node.id.replace('n',''),name:new_name,id:id};
                    treeobj.settings.data.opts.url = 'rename/';
                    treeobj.settings.data.opts.method = 'POST';
                    if(par!=-1) treeobj.refresh(par);
                    else treeobj.refresh();
                    return false;
                },
                beforedelete: function(node, treeobj) {
                    var par=treeobj.parent(node);
                    var id=(par==-1?0:par.attr('id').replace('n',''));
                    treeobj._params={node:node.id.replace('n',''),id:id};
                    treeobj.settings.data.opts.url = 'remove/';
                    treeobj.settings.data.opts.method = 'POST';
                    treeobj.refresh(par);
                    return false;
                },
                onsearch : function (n,t) {
		    t.container.find('.search').removeClass('search');
		    n.addClass('search');
		},
                ondata: function(data, treeobj) {
                    treeobj.settings.data.async=true;
                    treeobj.settings.data.opts.url='tree/';
                    //if(typeof(treeobj._params)!='undefined'){
                    treeobj._params=null;
                    treeobj.settings.data.opts.url='tree/';
                    treeobj.settings.data.opts.method='POST';
                    //}
                    /*if(treeobj.callback.afterdata){
                        treeobj.callback.afterdata();
                        treeobj.callback.afterdata=null;
                    }*/
                    return data;
                },
                beforedata: function(node, treeobj) {
                    treeobj.settings.data.async=true;
                    return (treeobj._params?treeobj._params:{'id':(node?$(node).attr('id').replace('n',''):0)});
                },
                onchange : function (node) {
                    document.location.href = $(node).children("a:eq(0)").attr("href");
                }

            },
            data: {
                type: "html",async: false
            },
            rules: {
                multiple:false
            },
            "types": {
                "default": permissions
            }
        });
    });
    $('#changelist').removeClass('module');

});

