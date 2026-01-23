import pickle
import tkinter as tk

class ProjectState:
    @staticmethod
    def save_project(filepath, main_controller):
        """
        Captures the entire state of the application into a dictionary.
        """
        view = main_controller.view
        
        # Helper to extract Treeview data
        def _extract_tree(tree):
            return [tree.item(i)['values'] for i in tree.get_children()]

        # 1. Base Data & Regression
        state = {
            "version": "2.0",
            "dataframe": main_controller.data_handler.get_data(),
            "regression_config": {
                "y_col": view.tab_data.combo_y.get(),
                "x_indices": view.tab_data.listbox_x.curselection(),
                "log_global": view.tab_data.var_log_global.get()
            },
            # 2. Settings (Dictionary from tab)
            "settings": view.tab_settings.get_settings(),
            
            # 3. Evolutionary Method
            "evolutionary": {
                "terreno": view.tab_evolutionary.sub_sum.ent_terr.get(),
                "fc": view.tab_evolutionary.sub_sum.ent_fc.get(),
                "principal_rows": _extract_tree(view.tab_evolutionary.sub_const.tree),
                "complementary_rows": _extract_tree(view.tab_evolutionary.sub_comp.tree)
            },
            
            # 4. Factors Method
            "factors": {
                "paradigma_prof": view.tab_factors.sub_setup.ent_prof.get(),
                "paradigma_topo": view.tab_factors.sub_setup.cb_topo.get(),
                "grid_rows": _extract_tree(view.tab_factors.sub_grid.tree)
            },
            
            # 5. Map Target
            "map_target": main_controller.current_map_target
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)

    @staticmethod
    def load_project(filepath, main_controller):
        """
        Restores the state.
        """
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
            
        view = main_controller.view
        
        # Helpers to restore UI
        def _set_entry(entry, val):
            entry.delete(0, tk.END)
            entry.insert(0, str(val))
            
        def _populate_tree(tree, rows):
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)

        # 1. Restore Dataframe
        if state.get("dataframe") is not None:
            main_controller.data_handler.df = state["dataframe"]
            main_controller.data_controller.atualizar_view()

        # 2. Restore Regression Config
        reg = state.get("regression", {})
        view.tab_data.combo_y.set(reg.get("y_col", ""))
        view.tab_data.var_log_global.set(reg.get("log_global", False))
        
        # Restore Listbox Selection
        lb = view.tab_data.listbox_x
        lb.selection_clear(0, tk.END)
        for idx in reg.get("x_indices", []):
            lb.selection_set(idx)

        # 3. Restore Settings
        s = state.get("settings", {})
        # Identification
        _set_entry(view.tab_settings.sub_ident.ent_name, s.get("avaliador", ""))
        _set_entry(view.tab_settings.sub_ident.ent_title, s.get("titulo_laudo", "")) # Note key matches SettingsIdentSubTab
        _set_entry(view.tab_settings.sub_ident.ent_job, s.get("titulo_profissional", ""))
        _set_entry(view.tab_settings.sub_ident.ent_crea, s.get("crea", ""))
        _set_entry(view.tab_settings.sub_ident.ent_company, s.get("empresa", ""))
        _set_entry(view.tab_settings.sub_ident.ent_city, s.get("cidade", ""))
        
        # Stats Settings
        view.tab_settings.sub_stats.sp_zscore.set(s.get("z_score_limit", 2.0))
        # (Combos require mapping back from values, simplified here)
        
        # Engineering Settings
        view.tab_settings.sub_eng.sp_kmin.set(s.get("k_min", 0.20))

        # 4. Restore Evolutionary
        evol = state.get("evolutionary", {})
        _set_entry(view.tab_evolutionary.sub_sum.ent_terr, evol.get("terreno", "0.00"))
        _set_entry(view.tab_evolutionary.sub_sum.ent_fc, evol.get("fc", "1.00"))
        _populate_tree(view.tab_evolutionary.sub_const.tree, evol.get("principal_rows", []))
        _populate_tree(view.tab_evolutionary.sub_comp.tree, evol.get("complementary_rows", []))

        # 5. Restore Factors
        fac = state.get("factors", {})
        _set_entry(view.tab_factors.sub_setup.ent_prof, fac.get("paradigma_prof", "30.00"))
        view.tab_factors.sub_setup.cb_topo.set(fac.get("paradigma_topo", "Plano"))
        _populate_tree(view.tab_factors.sub_grid.tree, fac.get("grid_rows", []))

        # 6. Restore Map Target
        main_controller.current_map_target = state.get("map_target")