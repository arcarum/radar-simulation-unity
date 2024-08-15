using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;   

public class ScenarioMenuUI
{
    VisualElement ui;
    MainMenuController mainMenuController;
    ShipManager shipManager;

    public ScenarioMenuUI(VisualElement ui, MainMenuController mainMenuController, ShipManager shipManager)
    {
        this.ui = ui;
        this.mainMenuController = mainMenuController;
        this.shipManager = shipManager;
    }

    public void SetBtnEvents()
    {
        // Ship Mangaer
        Button resetBtn = ui.Q("ResetBtn") as Button;
        resetBtn.RegisterCallback((ClickEvent clickEvent) => shipManager.resetScenario = !shipManager.resetScenario);

        Button reloadBtn = ui.Q("ReloadBtn") as Button;
        resetBtn.RegisterCallback((ClickEvent clickEvent) => shipManager.reloadCSV = !shipManager.reloadCSV);

        Button loadBtn = ui.Q("LoadBtn") as Button;
        loadBtn.RegisterCallback((ClickEvent clickEvent) => shipManager.loadScenario = !shipManager.loadScenario);

        // TODO: Reset toggle after resetting a scenario to be inline with ship manager
        Toggle logToggle = ui.Q("LogToggle") as Toggle;
        logToggle.RegisterCallback((ClickEvent clickEvent) => shipManager.logMessages = !shipManager.logMessages);

        SetDropdownField();
    }

    public void SetDropdownField()
    {
        DropdownField dropdownField = ui.Q("ScenarioDropdown") as DropdownField;
        
        List<string> files = shipManager.ReadScenarioFiles(out int numberOfNextScenario);
        mainMenuController.PassNextScenarioNumber(numberOfNextScenario);

        if (files.Count == 0)
        {
            Debug.Log("No scenario files found.");
            return; 
        }

        dropdownField.choices = files;
        dropdownField.value = shipManager.scenarioFileName = files[0];
        dropdownField.focusable = false;
        dropdownField.RegisterValueChangedCallback(evt => {
            shipManager.scenarioFileName = evt.newValue;
        });
    }
}