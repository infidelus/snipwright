<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de_DE">
<context>
    <name>ActionBar</name>
    <message>
        <location filename="../ui/transport_panel.py" line="871"/>
        <location filename="../ui/transport_panel.py" line="939"/>
        <source>Add Selection</source>
        <translation>Auswahl hinzufügen</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="875"/>
        <location filename="../ui/transport_panel.py" line="944"/>
        <source>Add Unselected</source>
        <translation>Nicht ausgewählte hinzufügen</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="879"/>
        <source>Save Video</source>
        <translation>Video speichern</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="928"/>
        <source>Cut Selection</source>
        <translation>Auswahl herausschneiden</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="930"/>
        <source>Cut the marked section out of the programme</source>
        <translation>Den markierten Abschnitt aus der Sendung herausschneiden</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="933"/>
        <source>Trim Unselected</source>
        <translation>Nicht Ausgewähltes entfernen</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="935"/>
        <source>Keep only the marked section, cutting everything outside it</source>
        <translation>Nur den markierten Abschnitt behalten und alles außerhalb herausschneiden</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="941"/>
        <source>Keep the marked section</source>
        <translation>Den markierten Abschnitt behalten</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="946"/>
        <source>Keep everything that isn&apos;t already selected</source>
        <translation>Alles behalten, was noch nicht ausgewählt ist</translation>
    </message>
</context>
<context>
    <name>AdDetectionPage</name>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="49"/>
        <source>Chalkline (built in)</source>
        <translation>Chalkline (integriert)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="50"/>
        <source>Comskip (external program)</source>
        <translation>Comskip (externes Programm)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="56"/>
        <source>Which detector finds the advert breaks, in the editor and the Watcher alike.</source>
        <translation>Welcher Detektor die Werbeunterbrechungen findet – im Editor ebenso wie im Watcher.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="62"/>
        <source>Chalkline</source>
        <translation>Chalkline</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="66"/>
        <source>Built into Snipwright, so there is nothing to install or configure. It reads the channel logo, the picture shape and the aspect ratio, and reports nothing at all when it cannot tell - rather than guessing and removing part of the programme.</source>
        <translation>In Snipwright integriert, es ist also nichts zu installieren oder einzurichten. Chalkline wertet das Senderlogo, die Bildform und das Seitenverhältnis aus und meldet lieber gar nichts, wenn es sich nicht sicher ist – statt zu raten und einen Teil der Sendung zu entfernen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="73"/>
        <source>Learn channel logos from my edits</source>
        <translation>Senderlogos aus meinen Bearbeitungen lernen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="78"/>
        <source>After you correct a detection and save the project, Chalkline remembers what that channel&apos;s logo looks like and finds the breaks better on the next recording from it. It only ever learns from a project you have edited yourself, never from its own unattended results.</source>
        <translation>Wenn Sie eine Erkennung korrigieren und das Projekt speichern, merkt sich Chalkline, wie das Logo dieses Senders aussieht, und findet die Unterbrechungen bei der nächsten Aufnahme dieses Senders besser. Gelernt wird ausschließlich aus einem Projekt, das Sie selbst bearbeitet haben, niemals aus den eigenen unbeaufsichtigten Ergebnissen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="85"/>
        <source>Remembered logos…</source>
        <translation>Gemerkte Logos…</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="94"/>
        <source>See what Chalkline has learned, pair a channel name with the service number the other recorder gives it, or forget a logo so it is learned afresh.</source>
        <translation>Sehen Sie, was Chalkline gelernt hat, verknüpfen Sie einen Sendernamen mit der Dienstnummer, die das andere Aufnahmegerät ihm gibt, oder verwerfen Sie ein Logo, damit es neu gelernt wird.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="101"/>
        <source>Comskip</source>
        <translation>Comskip</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="121"/>
        <source>Comskip is a separate program you install yourself. The .ini is optional - leave it blank to use Comskip&apos;s built-in defaults.</source>
        <translation>Comskip ist ein eigenständiges Programm, das Sie selbst installieren. Die .ini-Datei ist optional – lassen Sie das Feld leer, um die integrierten Standardwerte von Comskip zu verwenden.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="126"/>
        <source>Pick the .ini by channel name in the filename</source>
        <translation>Die .ini-Datei anhand des Sendernamens im Dateinamen auswählen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="133"/>
        <source>For recorders that write the channel into the filename (e.g. Tvheadend). Put per-channel files named Comskip_&lt;channel&gt;.ini in the same folder as the .ini above. See the user guide for details.</source>
        <translation>Für Aufnahmegeräte, die den Sender in den Dateinamen schreiben (z. B. Tvheadend). Legen Sie senderspezifische Dateien mit dem Namen Comskip_&lt;Sender&gt;.ini in denselben Ordner wie die obige .ini-Datei. Weitere Details finden Sie im Benutzerhandbuch.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="106"/>
        <source>Comskip program:</source>
        <translation>Comskip-Programm:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="108"/>
        <source>(path to the comskip executable)</source>
        <translation>(Pfad zur ausführbaren Comskip-Datei)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="114"/>
        <source>Comskip .ini:</source>
        <translation>Comskip-.ini:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="116"/>
        <source>(optional: path to comskip.ini)</source>
        <translation>(optional: Pfad zur comskip.ini)</translation>
    </message>
</context>
<context>
    <name>BatchManager</name>
    <message>
        <location filename="../ui/batch_manager.py" line="42"/>
        <source>Repairing</source>
        <translation>Reparieren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="43"/>
        <source>Indexing</source>
        <translation>Indizieren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="44"/>
        <source>Copying</source>
        <translation>Kopieren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="45"/>
        <source>Encoding</source>
        <translation>Kodieren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="46"/>
        <source>Verifying</source>
        <translation>Überprüfen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="47"/>
        <source>Recoding audio</source>
        <translation>Audio neu kodieren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="48"/>
        <source>Repairing audio</source>
        <translation>Audio wird repariert</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="49"/>
        <source>Repackaging</source>
        <translation>Neu verpacken</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="50"/>
        <source>Recoding</source>
        <translation>Neu kodieren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="51"/>
        <source>Rebuilding audio</source>
        <translation>Audio neu aufbauen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="52"/>
        <source>Copying audio</source>
        <translation>Audio wird kopiert</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="53"/>
        <source>Finalising</source>
        <translation>Wird abgeschlossen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="54"/>
        <source>Finishing</source>
        <translation>Fertigstellen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="59"/>
        <location filename="../ui/batch_manager.py" line="700"/>
        <source>Queued</source>
        <translation>In der Warteschlange</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="60"/>
        <source>Done</source>
        <translation>Fertig</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="61"/>
        <source>Failed</source>
        <translation>Fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="62"/>
        <source>Cancelled</source>
        <translation>Abgebrochen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="63"/>
        <source>Needs review</source>
        <translation>Überprüfung erforderlich</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="912"/>
        <source>Working</source>
        <translation>In Arbeit</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="55"/>
        <source>Joining</source>
        <translation>Zusammenfügen</translation>
    </message>
</context>
<context>
    <name>BatchManagerDialog</name>
    <message>
        <location filename="../ui/batch_manager.py" line="81"/>
        <location filename="../ui/batch_manager.py" line="812"/>
        <location filename="../ui/batch_manager.py" line="819"/>
        <location filename="../ui/batch_manager.py" line="826"/>
        <source>Batch Manager</source>
        <translation>Stapelverwaltung</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="119"/>
        <source>Output folder:</source>
        <translation>Ausgabeordner:</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="123"/>
        <source>Browse…</source>
        <translation>Durchsuchen…</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="128"/>
        <source>Default profile:</source>
        <translation>Standardprofil:</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="139"/>
        <source>Name modifier:</source>
        <translation>Namensmodifikator:</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="142"/>
        <source>optional - prefixes the name, or suffixes it if it starts with - or _</source>
        <translation>optional - stellt dem Namen ein Präfix voran, oder ein Suffix hintenan, wenn es mit - oder _ beginnt</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="157"/>
        <source>Project</source>
        <translation>Projekt</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="157"/>
        <source>Profile</source>
        <translation>Profil</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="157"/>
        <source>Output</source>
        <translation>Ausgabe</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="158"/>
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="174"/>
        <source>Add Projects…</source>
        <translation>Projekte hinzufügen…</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="176"/>
        <location filename="../ui/batch_manager.py" line="418"/>
        <location filename="../ui/batch_manager.py" line="466"/>
        <location filename="../ui/batch_manager.py" line="482"/>
        <source>Add from Watch Folder</source>
        <translation>Aus Überwachungsordner hinzufügen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="178"/>
        <source>Add new projects produced by the Snipwright Watcher (commercial detection). They arrive stopped, for you to review and Start.</source>
        <translation>Fügt neue Projekte hinzu, die vom Snipwright Watcher (Werbeerkennung) erstellt wurden. Sie werden im gestoppten Zustand hinzugefügt, damit Sie sie überprüfen und starten können.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="182"/>
        <location filename="../ui/batch_manager.py" line="548"/>
        <source>Remove</source>
        <translation>Entfernen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="184"/>
        <source>Move Up</source>
        <translation>Nach oben</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="186"/>
        <source>Move Down</source>
        <translation>Nach unten</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="188"/>
        <source>Send to End</source>
        <translation>Ans Ende verschieben</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="190"/>
        <source>Move this job to the back of the queue. Useful when a job was held or failed, the batch has moved past it, and you&apos;ve since fixed it - sending it to the end puts it back in this run rather than waiting for the queue to finish.</source>
        <translation>Verschiebt diesen Auftrag ans Ende der Warteschlange. Praktisch, wenn ein Auftrag zurückgestellt wurde oder fehlgeschlagen ist, der Stapel bereits daran vorbei ist und Sie ihn inzwischen behoben haben – ans Ende verschoben kommt er noch in diesem Durchlauf an die Reihe, statt auf das Ende der Warteschlange zu warten.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="200"/>
        <source>Clear Finished</source>
        <translation>Abgeschlossene leeren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="228"/>
        <location filename="../ui/batch_manager.py" line="833"/>
        <location filename="../ui/batch_manager.py" line="845"/>
        <source>Start</source>
        <translation>Starten</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="231"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="315"/>
        <source>No favourite folders set</source>
        <translation>Keine Favoriten-Ordner festgelegt</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="312"/>
        <source>%s (not available)</source>
        <translation>%s (nicht verfügbar)</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="158"/>
        <source>Folder</source>
        <translation>Ordner</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="291"/>
        <source>Default</source>
        <translation>Standard</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="293"/>
        <source>Uses the batch&apos;s output folder. Choose a favourite to send this one job somewhere else.</source>
        <translation>Verwendet den Ausgabeordner des Stapels. Wähle einen Favoriten, um nur diesen einen Auftrag woanders zu speichern.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="297"/>
        <source>Default (batch output folder)</source>
        <translation>Standard (Ausgabeordner des Stapels)</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="333"/>
        <source>Output Folder</source>
        <translation>Ausgabeordner</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="354"/>
        <source>%s (missing)</source>
        <translation>%s (fehlt)</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="390"/>
        <source>…and %d more</source>
        <translation>…und %d weitere</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="393"/>
        <source>Add Projects</source>
        <translation>Projekte hinzufügen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="394"/>
        <source>%d of the selected projects are already in the queue:

%s

Add them again?</source>
        <translation>%d der ausgewählten Projekte sind bereits in der Warteschlange:

%s

Erneut hinzufügen?</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="398"/>
        <source>&quot;%s&quot; is already in the queue.

Add it again?</source>
        <translation>&quot;%s&quot; ist bereits in der Warteschlange.

Erneut hinzufügen?</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="419"/>
        <source>The watch output folder doesn&apos;t exist yet. Set it up in the Snipwright Watcher first.</source>
        <translation>Der Überwachungs-Ausgabeordner existiert noch nicht. Richten Sie ihn zuerst im Snipwright Watcher ein.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="467"/>
        <source>No new projects in the watch folder — everything there is already in the queue.</source>
        <translation>Keine neuen Projekte im Überwachungsordner — alles dort befindet sich bereits in der Warteschlange.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="474"/>
        <source>Added %d project(s) from the watch folder. They&apos;re queued and stopped — review each with Edit, then Start.</source>
        <translation>%d Projekt(e) aus dem Überwachungsordner hinzugefügt. Sie befinden sich gestoppt in der Warteschlange — prüfen Sie jedes mit Bearbeiten und starten Sie dann.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="479"/>
        <source>Skipped %d already in the queue.</source>
        <translation>%d übersprungen, die bereits in der Warteschlange sind.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="499"/>
        <source>Working from:  %s</source>
        <translation>Arbeitet von:  %s</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="521"/>
        <source>Stop export</source>
        <translation>Export stoppen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="522"/>
        <source>%d export(s) are still being written in the background:

%s

Stopping now discards the part-finished file. The rows disappear once the encoder has actually stopped, which can take a moment.

Stop them?</source>
        <translation>%d Export(e) werden noch im Hintergrund geschrieben:

%s

Beim Stoppen wird die unfertige Datei verworfen. Die Zeilen verschwinden erst, wenn der Encoder tatsächlich angehalten hat – das kann einen Moment dauern.

Stoppen?</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="549"/>
        <source>That file is being processed right now. Stop the batch first if you want to remove it.</source>
        <translation>Diese Datei wird gerade verarbeitet. Beenden Sie zuerst die Stapelverarbeitung, wenn Sie sie entfernen möchten.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="648"/>
        <source>Edit…</source>
        <translation>Bearbeiten…</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="691"/>
        <source>Exporting… %d%%</source>
        <translation>Exportiert… %d %%</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="693"/>
        <source>Running… %d%%</source>
        <translation>Läuft… %d%%</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="695"/>
        <source>Needs review — Edit to repair &amp; confirm</source>
        <translation>Überprüfung erforderlich — Bearbeiten zum Reparieren &amp; Bestätigen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="731"/>
        <location filename="../ui/batch_manager.py" line="742"/>
        <source>Edit</source>
        <translation>Bearbeiten</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="773"/>
        <source>Stop Batch</source>
        <translation>Stapelverarbeitung beenden</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="774"/>
        <source>Stop processing the queue?</source>
        <translation>Verarbeitung der Warteschlange beenden?</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="776"/>
        <source>The job that&apos;s currently running can be finished first, or stopped straight away and left unfinished.</source>
        <translation>Der gerade laufende Auftrag kann zuerst abgeschlossen oder sofort beendet und unvollendet gelassen werden.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="783"/>
        <source>This affects the batch only. An export sent here from the editor keeps running either way - to stop that, select its row and press Remove.</source>
        <translation>Das betrifft nur den Stapel. Ein aus dem Editor hierher gesendeter Export läuft in beiden Fällen weiter – um ihn zu stoppen, wähle seine Zeile aus und drücke „Entfernen“.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="789"/>
        <source>Finish current file, then stop</source>
        <translation>Aktuelle Datei abschließen, dann beenden</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="791"/>
        <source>Stop now</source>
        <translation>Sofort beenden</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="792"/>
        <source>Keep going</source>
        <translation>Fortfahren</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="799"/>
        <location filename="../ui/batch_manager.py" line="853"/>
        <source>Stopping after the current file…</source>
        <translation>Beenden nach der aktuellen Datei…</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="687"/>
        <location filename="../ui/batch_manager.py" line="804"/>
        <source>Stopping…</source>
        <translation>Wird beendet…</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="812"/>
        <source>Add at least one project first.</source>
        <translation>Fügen Sie zuerst mindestens ein Projekt hinzu.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="827"/>
        <source>Every job is already done. Add more, or use Clear Finished.</source>
        <translation>Alle Aufträge sind bereits erledigt. Fügen Sie weitere hinzu oder nutzen Sie „Abgeschlossene leeren“.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="833"/>
        <location filename="../ui/batch_manager.py" line="845"/>
        <source>Stop</source>
        <translation>Stoppen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="856"/>
        <source>Batch running…</source>
        <translation>Stapelverarbeitung läuft…</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="935"/>
        <source>%s left</source>
        <translation>noch %s</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="960"/>
        <source>Stopped</source>
        <translation>Gestoppt</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="960"/>
        <source>Finished</source>
        <translation>Abgeschlossen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="971"/>
        <location filename="../ui/batch_manager.py" line="980"/>
        <source>Batch finished</source>
        <translation>Stapelverarbeitung abgeschlossen</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="732"/>
        <source>The project file no longer exists:

%s</source>
        <translation>Die Projektdatei existiert nicht mehr:

%s</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="972"/>
        <source>%(summary)s

%(held)d file(s) need repairing before they can be cut. Click Edit on each to run Quick Stream Fix and confirm the cut points, then run the batch again.</source>
        <translation>%(summary)s

%(held)d Datei(en) müssen repariert werden, bevor sie geschnitten werden können. Klicken Sie bei jeder auf Bearbeiten, um die Schnelle Stream-Reparatur auszuführen und die Schnittpunkte zu bestätigen, und starten Sie den Stapel dann erneut.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="981"/>
        <source>%s

See the Status column for what went wrong with the failed jobs.</source>
        <translation>%s

In der Spalte „Status“ steht, was bei den fehlgeschlagenen Aufträgen schiefgegangen ist.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="820"/>
        <source>%d job(s) are waiting for review. Click Edit on each to repair and confirm the cuts, then run the batch again.</source>
        <translation>%d Auftrag/Aufträge warten auf Ihre Prüfung. Klicken Sie bei jedem auf Bearbeiten, um zu reparieren und die Schnitte zu bestätigen, und starten Sie den Stapel dann erneut.</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="883"/>
        <source>Processing %(index)d of %(total)d: %(name)s</source>
        <translation>%(index)d von %(total)d wird verarbeitet: %(name)s</translation>
    </message>
    <message>
        <location filename="../ui/batch_manager.py" line="743"/>
        <source>This is a joined video queued from the Joiner. To change it, remove it from the queue, edit the Joiner list and queue it again.</source>
        <translation>Dies ist ein aus dem Joiner eingereihtes, zusammengefügtes Video. Um es zu ändern, entferne es aus der Warteschlange, bearbeite die Joiner-Liste und reihe sie erneut ein.</translation>
    </message>
</context>
<context>
    <name>Comskip</name>
    <message>
        <location filename="../repair/comskip.py" line="135"/>
        <source>Commercial detection cancelled.</source>
        <translation>Werbeerkennung abgebrochen.</translation>
    </message>
</context>
<context>
    <name>ConfigEditorDialog</name>
    <message>
        <location filename="../ui/config_editor.py" line="34"/>
        <source>Edit configuration</source>
        <translation>Konfiguration bearbeiten</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="41"/>
        <source>Editing the configuration file. It is checked for valid JSON before saving, and your changes are applied when you save.</source>
        <translation>Bearbeitung der Konfigurationsdatei. Vor dem Speichern wird sie auf gültiges JSON geprüft; Ihre Änderungen werden beim Speichern übernommen.</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="63"/>
        <source>Reload from disk</source>
        <translation>Von der Festplatte neu laden</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="70"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="75"/>
        <source>Save</source>
        <translation>Speichern</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="128"/>
        <source>Duplicate shortcut keys</source>
        <translation>Doppelte Tastenkürzel</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="131"/>
        <source>Duplicate shortcut keys - nothing was saved.</source>
        <translation>Doppelte Tastenkürzel - es wurde nichts gespeichert.</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="146"/>
        <source>Unrecognised shortcut keys</source>
        <translation>Unbekannte Tastenkürzel</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="153"/>
        <source>Unrecognised shortcut keys - nothing was saved.</source>
        <translation>Unbekannte Tastenkürzel - es wurde nichts gespeichert.</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="166"/>
        <source>Configuration saved</source>
        <translation>Konfiguration gespeichert</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="167"/>
        <source>The configuration has been saved and will be applied now.</source>
        <translation>Die Konfiguration wurde gespeichert und wird jetzt übernommen.</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="93"/>
        <source>Could not read the file: %s</source>
        <translation>Die Datei konnte nicht gelesen werden: %s</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="103"/>
        <source>Not valid JSON (line %(line)d, column %(col)d): %(msg)s. Nothing was saved.</source>
        <translation>Kein gültiges JSON (Zeile %(line)d, Spalte %(col)d): %(msg)s. Es wurde nichts gespeichert.</translation>
    </message>
    <message>
        <location filename="../ui/config_editor.py" line="161"/>
        <source>Could not save: %s</source>
        <translation>Speichern nicht möglich: %s</translation>
    </message>
</context>
<context>
    <name>CropPreviewDialog</name>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="126"/>
        <source>Crop preview</source>
        <translation>Zuschneide-Vorschau</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="148"/>
        <source>Loading…</source>
        <translation>Laden…</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="158"/>
        <source>Frame:</source>
        <translation>Bild:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="181"/>
        <source>Auto-detect</source>
        <translation>Automatisch erkennen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="207"/>
        <source>No recording open.</source>
        <translation>Keine Aufnahme geöffnet.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="233"/>
        <source>Couldn&apos;t read a frame here.</source>
        <translation>Bild konnte an dieser Stelle nicht gelesen werden.</translation>
    </message>
</context>
<context>
    <name>ExportCompleteDialog</name>
    <message>
        <location filename="../ui/export_dialogs.py" line="284"/>
        <source>Output Processing Complete</source>
        <translation>Ausgabeverarbeitung abgeschlossen</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="375"/>
        <source>See the log for the full explanation.</source>
        <translation>Die vollständige Erklärung steht im Protokoll.</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="432"/>
        <source>Open Folder</source>
        <translation>Ordner öffnen</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="439"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="301"/>
        <source>Video length:</source>
        <translation>Videolänge:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="303"/>
        <source>Video size:</source>
        <translation>Videogröße:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="305"/>
        <source>Output scenes:</source>
        <translation>Ausgegebene Szenen:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="307"/>
        <source>Video output frames:</source>
        <translation>Ausgegebene Videobilder:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="309"/>
        <source>Audio output frames:</source>
        <translation>Ausgegebene Audio-Frames:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="311"/>
        <source>Audio tracks:</source>
        <translation>Audiospuren:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="316"/>
        <source>Subtitles:</source>
        <translation>Untertitel:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="319"/>
        <source>Processing time:</source>
        <translation>Verarbeitungszeit:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="321"/>
        <source>Processed frames/sec:</source>
        <translation>Verarbeitete Bilder/s:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="323"/>
        <source>Video bitrate:</source>
        <translation>Videobitrate:</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="269"/>
        <source>None</source>
        <translation>Keine</translation>
    </message>
</context>
<context>
    <name>ExportNotes</name>
    <message>
        <location filename="../export/exporter.py" line="3552"/>
        <source>%s - see logs</source>
        <translation>%s – siehe Protokoll</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3558"/>
        <source>%d subtitle track not carried over</source>
        <translation>%d Untertitelspur nicht übernommen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3559"/>
        <source>%d subtitle tracks not carried over</source>
        <translation>%d Untertitelspuren nicht übernommen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3562"/>
        <source>%d audio track could not be written</source>
        <translation>%d Audiospur konnte nicht geschrieben werden</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3563"/>
        <source>%d audio tracks could not be written</source>
        <translation>%d Audiospuren konnten nicht geschrieben werden</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3566"/>
        <source>%d silent audio track not carried over</source>
        <translation>%d stumme Audiospur nicht übernommen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3567"/>
        <source>%d silent audio tracks not carried over</source>
        <translation>%d stumme Audiospuren nicht übernommen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3570"/>
        <source>%d audio-description track not carried over</source>
        <translation>%d Audiodeskriptionsspur nicht übernommen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3571"/>
        <source>%d audio-description tracks not carried over</source>
        <translation>%d Audiodeskriptionsspuren nicht übernommen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3574"/>
        <source>%d empty audio track skipped</source>
        <translation>%d leere Audiospur übersprungen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3575"/>
        <source>%d empty audio tracks skipped</source>
        <translation>%d leere Audiospuren übersprungen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3578"/>
        <source>%d audio track missing</source>
        <translation>%d Audiospur fehlt</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3579"/>
        <source>%d audio tracks missing</source>
        <translation>%d Audiospuren fehlen</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3581"/>
        <source>a few audio frames were re-encoded</source>
        <translation>einige Audio-Frames wurden neu kodiert</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3582"/>
        <source>audio missing from the MP4</source>
        <translation>Audio fehlt in der MP4</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3583"/>
        <source>audio adjustment not applied</source>
        <translation>Audioanpassung nicht angewendet</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3584"/>
        <source>output has no audio</source>
        <translation>Ausgabe hat kein Audio</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3585"/>
        <source>repackaged audio</source>
        <translation>Audio neu verpackt</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3586"/>
        <source>output ~%.1fs shorter than the edit</source>
        <translation>Ausgabe ~%.1f s kürzer als der Schnitt</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3587"/>
        <source>output ~%.1fs longer than the edit</source>
        <translation>Ausgabe ~%.1f s länger als der Schnitt</translation>
    </message>
    <message>
        <location filename="../export/exporter.py" line="3588"/>
        <source>video could not be re-encoded - the file is in the original codec, not the one the profile asked for</source>
        <translation>Video konnte nicht neu kodiert werden – die Datei liegt im Originalcodec vor, nicht in dem vom Profil verlangten</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="60"/>
        <source>Rendering scene %d of %d…</source>
        <translation>Szene %d von %d wird erstellt…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="61"/>
        <source>Re-encoding and joining scenes…</source>
        <translation>Szenen werden neu kodiert und zusammengefügt…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="62"/>
        <source>Applying profile…</source>
        <translation>Profil wird angewendet…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="63"/>
        <source>Writing MKV…</source>
        <translation>MKV wird geschrieben…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="64"/>
        <source>Converting to MP4…</source>
        <translation>Wird in MP4 umgewandelt…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="394"/>
        <source>%s  (about %s left)</source>
        <translation>%s  (noch etwa %s)</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="493"/>
        <source>Building title card %d of %d…</source>
        <translation>Titeleinblendung %d von %d wird erstellt…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="557"/>
        <source>Joining scenes…</source>
        <translation>Szenen werden zusammengefügt…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="589"/>
        <source>Done</source>
        <translation>Fertig</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="743"/>
        <source>some audio tracks could not be carried through</source>
        <translation>einige Audiospuren konnten nicht übernommen werden</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="785"/>
        <location filename="../export/joiner_render.py" line="933"/>
        <source>some subtitles could not be carried through</source>
        <translation>einige Untertitel konnten nicht übernommen werden</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="822"/>
        <source>the scenes were re-encoded to join them</source>
        <translation>die Szenen wurden zum Zusammenfügen neu kodiert</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="954"/>
        <source>Adding subtitles…</source>
        <translation>Untertitel werden hinzugefügt…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="963"/>
        <source>subtitles could not be carried through</source>
        <translation>Untertitel konnten nicht übernommen werden</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="975"/>
        <source>disc subtitles were converted</source>
        <translation>Disc-Untertitel wurden umgewandelt</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="985"/>
        <source>subtitles were redrawn to fit</source>
        <translation>Untertitel wurden passend neu gezeichnet</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="1220"/>
        <source>Checking MKV audio…</source>
        <translation>MKV-Audio wird geprüft…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="1221"/>
        <source>Comparing against the source audio…</source>
        <translation>Abgleich mit dem Quell-Audio…</translation>
    </message>
    <message>
        <location filename="../export/joiner_render.py" line="1222"/>
        <source>Rebuilding MKV audio…</source>
        <translation>MKV-Audio wird neu aufgebaut…</translation>
    </message>
</context>
<context>
    <name>ExportProgressDialog</name>
    <message>
        <location filename="../ui/export_dialogs.py" line="90"/>
        <source>Exporting</source>
        <translation>Export läuft</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="109"/>
        <source>Estimated time remaining: —</source>
        <translation>Geschätzte Restzeit: —</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="113"/>
        <source>Preparing…</source>
        <translation>Wird vorbereitet…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="122"/>
        <source>Send to Batch</source>
        <translation>An Stapel senden</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="125"/>
        <source>Hand this export to the Batch Manager and carry on working. It keeps running from where it is - nothing restarts, and the file still goes where you asked.</source>
        <translation>Übergibt diesen Export an den Batch-Manager, sodass Sie weiterarbeiten können. Er läuft an der Stelle weiter, an der er gerade ist – nichts beginnt von vorn, und die Datei wird weiterhin dort gespeichert, wo Sie es angegeben haben.</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="132"/>
        <source>Abort</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="183"/>
        <source>Aborting…</source>
        <translation>Wird abgebrochen…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="219"/>
        <location filename="../ui/export_dialogs.py" line="245"/>
        <source>Estimated time remaining: …</source>
        <translation>Geschätzte Restzeit: …</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="243"/>
        <source>Estimated time remaining: done</source>
        <translation>Geschätzte Restzeit: fertig</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="233"/>
        <source>Scene %(scene)d of %(total)d</source>
        <translation>Szene %(scene)d von %(total)d</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="30"/>
        <source>Working…</source>
        <translation>Wird verarbeitet…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="32"/>
        <source>Fast Frame Copy</source>
        <translation>Schnelle Frame-Kopie</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="33"/>
        <source>Encoding Frames</source>
        <translation>Frames werden kodiert</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="34"/>
        <source>Cropping (re-encoding)…</source>
        <translation>Zuschneiden (Neukodierung)…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="35"/>
        <source>Verifying output</source>
        <translation>Ausgabe wird überprüft</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="36"/>
        <source>Finalising MKV…</source>
        <translation>MKV wird abgeschlossen…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="37"/>
        <source>Recoding…</source>
        <translation>Wird neu kodiert…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="41"/>
        <source>Repairing audio…</source>
        <translation>Audio wird repariert…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="45"/>
        <source>Repackaging to MP4…</source>
        <translation>Wird neu in MP4 verpackt…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="46"/>
        <source>Major recode required…</source>
        <translation>Umfassende Neukodierung erforderlich…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="47"/>
        <source>Rebuilding audio…</source>
        <translation>Audio wird neu aufgebaut…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="48"/>
        <source>Copying audio…</source>
        <translation>Audio wird kopiert…</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="49"/>
        <source>Finishing</source>
        <translation>Wird fertiggestellt</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="239"/>
        <source>Estimated time remaining: %s</source>
        <translation>Geschätzte Restzeit: %s</translation>
    </message>
    <message>
        <location filename="../ui/export_dialogs.py" line="201"/>
        <source>Joining…</source>
        <translation>Zusammenfügen…</translation>
    </message>
</context>
<context>
    <name>FileRow</name>
    <message>
        <location filename="../ui/settings_widgets.py" line="173"/>
        <source>Browse…</source>
        <translation>Durchsuchen…</translation>
    </message>
    <message>
        <location filename="../ui/settings_widgets.py" line="185"/>
        <source>Choose file</source>
        <translation>Datei auswählen</translation>
    </message>
</context>
<context>
    <name>FilesPage</name>
    <message>
        <location filename="../ui/settings_pages/files.py" line="34"/>
        <source>Quick Stream Fix on open</source>
        <translation>Schnelle Stream-Reparatur beim Öffnen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="38"/>
        <source>When enabled, opened files are remuxed first to repair broken broadcast streams before loading.</source>
        <translation>Wenn aktiviert, werden geöffnete Dateien zuerst remuxt, um defekte Broadcast-Streams vor dem Laden zu reparieren.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="43"/>
        <source>Don&apos;t warn when re-running Quick Stream Fix</source>
        <translation>Nicht warnen, wenn die Schnelle Stream-Reparatur erneut ausgeführt wird</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="48"/>
        <source>Snipwright remembers files it has already Quick Stream Fixed and asks before repairing one again. Tick this to skip that prompt.</source>
        <translation>Snipwright merkt sich Dateien, die bereits mit der Schnellen Stream-Reparatur verarbeitet wurden, und fragt vor einer erneuten Reparatur nach. Aktivieren Sie dies, um diese Abfrage zu überspringen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="104"/>
        <source>Favourite folders</source>
        <translation>Favoriten-Ordner</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="106"/>
        <source>Folders offered under the Folders button when saving a video, for keeping different series on different drives. Drag to reorder.</source>
        <translation>Ordner, die beim Speichern eines Videos unter der Schaltfläche „Ordner“ angeboten werden – praktisch, wenn Sie verschiedene Serien auf verschiedenen Laufwerken ablegen. Zum Umsortieren ziehen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="122"/>
        <source>Add…</source>
        <translation>Hinzufügen…</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="125"/>
        <source>Remove</source>
        <translation>Entfernen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="133"/>
        <source>Add a favourite folder</source>
        <translation>Favoriten-Ordner hinzufügen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="55"/>
        <source>Opening videos:</source>
        <translation>Videos öffnen:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="62"/>
        <source>Saving videos:</source>
        <translation>Videos speichern:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="69"/>
        <source>Project files:</source>
        <translation>Projektdateien:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="82"/>
        <source>Project format:</source>
        <translation>Projektformat:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="85"/>
        <source>Snipwright (.swproj)</source>
        <translation>Snipwright (.swproj)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="87"/>
        <source>VideoReDo (.vprj)</source>
        <translation>VideoReDo (.vprj)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/files.py" line="95"/>
        <source>The format Save Project writes. A Snipwright project records which recording it belongs to and places its cuts on the exact frames you chose, but VideoReDo cannot open it - choose VideoReDo if you move projects between the two. Either kind opens in Snipwright, and Save Project As offers both.</source>
        <translation>Das Format, das „Projekt speichern“ schreibt. Ein Snipwright-Projekt vermerkt, zu welcher Aufnahme es gehört, und setzt seine Schnitte genau auf die gewählten Bilder, lässt sich aber nicht in VideoReDo öffnen – wähle VideoReDo, wenn du Projekte zwischen beiden austauschst. Beide Arten lassen sich in Snipwright öffnen, und „Projekt speichern unter“ bietet beide an.</translation>
    </message>
</context>
<context>
    <name>FilmRenamer</name>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="146"/>
        <source>no match — double-click to search</source>
        <translation>keine Übereinstimmung — Doppelklick zum Suchen</translation>
    </message>
</context>
<context>
    <name>FilmRenamerDialog</name>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="174"/>
        <location filename="../ui/film_renamer_dialog.py" line="329"/>
        <location filename="../ui/film_renamer_dialog.py" line="409"/>
        <location filename="../ui/film_renamer_dialog.py" line="455"/>
        <location filename="../ui/film_renamer_dialog.py" line="480"/>
        <location filename="../ui/film_renamer_dialog.py" line="730"/>
        <location filename="../ui/film_renamer_dialog.py" line="877"/>
        <location filename="../ui/film_renamer_dialog.py" line="898"/>
        <location filename="../ui/film_renamer_dialog.py" line="903"/>
        <source>Film Renamer</source>
        <translation>Film-Umbenenner</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="181"/>
        <source>Source</source>
        <translation>Quelle</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="183"/>
        <source>Choose Folder…</source>
        <translation>Ordner auswählen…</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="185"/>
        <source>Add Files…</source>
        <translation>Dateien hinzufügen…</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="187"/>
        <source>Refresh</source>
        <translation>Aktualisieren</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="188"/>
        <source>Re-scan the current folder for new files</source>
        <translation>Den aktuellen Ordner erneut nach neuen Dateien durchsuchen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="191"/>
        <source>No files chosen.</source>
        <translation>Keine Dateien ausgewählt.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="192"/>
        <source>Load last folder on open</source>
        <translation>Zuletzt verwendeten Ordner beim Öffnen laden</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="194"/>
        <source>When ticked, the renamer opens straight into the folder you used last.</source>
        <translation>Wenn aktiviert, öffnet sich der Umbenenner direkt in dem Ordner, den Sie zuletzt verwendet haben.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="215"/>
        <source>Preset:</source>
        <translation>Voreinstellung:</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="219"/>
        <source>Save…</source>
        <translation>Speichern…</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="221"/>
        <source>Save the current pattern as a named preset</source>
        <translation>Das aktuelle Muster als benannte Voreinstellung speichern</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="225"/>
        <source>Delete</source>
        <translation>Löschen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="226"/>
        <source>Delete the selected saved preset</source>
        <translation>Die ausgewählte gespeicherte Voreinstellung löschen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="233"/>
        <source>Pattern:</source>
        <translation>Muster:</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="240"/>
        <source>Codes…</source>
        <translation>Codes…</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="242"/>
        <source>Pattern codes</source>
        <translation>Mustercodes</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="245"/>
        <source>Match Films</source>
        <translation>Filme abgleichen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="261"/>
        <source>Destination:</source>
        <translation>Zielverzeichnis:</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="265"/>
        <source>Choose…</source>
        <translation>Auswählen…</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="267"/>
        <source>Clear</source>
        <translation>Leeren</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="281"/>
        <source>Overwrite files that already exist at the destination</source>
        <translation>Dateien überschreiben, die am Zielort bereits existieren</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="286"/>
        <source>Double-click a row to pick a different film for it.</source>
        <translation>Doppelklicken Sie auf eine Zeile, um einen anderen Film dafür auszuwählen.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="291"/>
        <source>Current name</source>
        <translation>Aktueller Name</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="291"/>
        <source>New name</source>
        <translation>Neuer Name</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="291"/>
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="306"/>
        <source>Process Ticked</source>
        <translation>Ausgewählte verarbeiten</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="309"/>
        <source>Clear Completed</source>
        <translation>Abgeschlossene leeren</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="312"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="330"/>
        <source>No TMDB API key set. Add one in Settings (the TMDB API key field on the General page), then try again.</source>
        <translation>Kein TMDB-API-Schlüssel festgelegt. Fügen Sie einen in den Einstellungen hinzu (das Feld TMDB-API-Schlüssel auf der Registerkarte Allgemein) und versuchen Sie es erneut.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="386"/>
        <source>Choose folder</source>
        <translation>Ordner auswählen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="409"/>
        <source>No video files found in that folder.</source>
        <translation>Keine Videodateien in diesem Ordner gefunden.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="455"/>
        <source>Choose some files first.</source>
        <translation>Wählen Sie zuerst einige Dateien aus.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="564"/>
        <source>Custom…</source>
        <translation>Benutzerdefiniert…</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="586"/>
        <location filename="../ui/film_renamer_dialog.py" line="590"/>
        <source>Save preset</source>
        <translation>Voreinstellung speichern</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="586"/>
        <source>There&apos;s no pattern to save.</source>
        <translation>Es gibt kein Muster zum Speichern.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="590"/>
        <source>Name for this preset:</source>
        <translation>Name für dieses Preset:</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="620"/>
        <source>Delete preset</source>
        <translation>Voreinstellung löschen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="650"/>
        <source>e.g.   %s</source>
        <translation>z. B.   %s</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="672"/>
        <source>Choose destination library folder</source>
        <translation>Ziel-Bibliotheksordner auswählen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="713"/>
        <source>Choose film</source>
        <translation>Film auswählen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="743"/>
        <source>Search</source>
        <translation>Suchen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="781"/>
        <source>Done</source>
        <translation>Fertig</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="785"/>
        <source>not matched yet</source>
        <translation>noch nicht abgeglichen</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="787"/>
        <source>Rename Not Required</source>
        <translation>Umbenennung nicht erforderlich</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="788"/>
        <source>Ready</source>
        <translation>Bereit</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="877"/>
        <source>Nothing is ticked to rename.</source>
        <translation>Es ist nichts zum Umbenennen ausgewählt.</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="621"/>
        <source>Delete the preset &apos;%s&apos;?</source>
        <translation>Die Voreinstellung „%s“ löschen?</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="850"/>
        <source>%(ready)d ready · %(done)d done · %(total)d total</source>
        <translation>%(ready)d bereit · %(done)d erledigt · %(total)d gesamt</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="904"/>
        <source>Renamed %d film(s).%s%s</source>
        <translation>%d Film(e) umbenannt.%s%s</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="907"/>
        <source>
Skipped %d (target already exists).</source>
        <translation>
%d übersprungen (Ziel existiert bereits).</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="909"/>
        <source>
Failed %d.</source>
        <translation>
%d fehlgeschlagen.</translation>
    </message>
</context>
<context>
    <name>GeneralPage</name>
    <message>
        <location filename="../ui/settings_pages/general.py" line="36"/>
        <source>Editing mode:</source>
        <translation>Bearbeitungsmodus:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="56"/>
        <source>Show tooltips on the transport controls</source>
        <translation>Tooltips auf den Wiedergabesteuerungen anzeigen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="60"/>
        <source>Hover hints on the play, skip and marker buttons. Turn off once you know the controls.</source>
        <translation>Kurzinfos für die Wiedergabe-, Sprung- und Markierungsschaltflächen. Schalten Sie sie aus, sobald Sie die Bedienelemente kennen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="50"/>
        <source>Cut Mode starts with the whole programme selected and you cut the unwanted parts out of it. Scene Mode starts with nothing selected and you mark the parts you want to keep. Switching updates the buttons and scene list at once; the next video you open starts in the new mode.</source>
        <translation>Im Schnittmodus ist zunächst die gesamte Sendung ausgewählt und Sie schneiden die unerwünschten Teile heraus. Im Szenenmodus ist zunächst nichts ausgewählt und Sie markieren die Teile, die Sie behalten möchten. Ein Wechsel aktualisiert die Schaltflächen und die Szenenliste sofort; das nächste geöffnete Video startet im neuen Modus.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="77"/>
        <source> seconds</source>
        <translation> Sekunden</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="87"/>
        <source>Reset skip distances</source>
        <translation>Sprungweiten zurücksetzen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="70"/>
        <source>Short skip (keyboard only):</source>
        <translation>Kurzer Sprung (nur Tastatur):</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="72"/>
        <source>Medium skip (inner buttons):</source>
        <translation>Mittlerer Sprung (innere Schaltflächen):</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="74"/>
        <source>Long skip (outer buttons):</source>
        <translation>Langer Sprung (äußere Schaltflächen):</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="93"/>
        <source>How far the skip controls move through a recording. The buttons&apos; hover hints update to match. See the User Guide for the keyboard shortcuts each one uses.</source>
        <translation>Wie weit sich die Sprungsteuerung durch eine Aufnahme bewegt. Die Kurzinfos der Schaltflächen passen sich an. Die zugehörigen Tastenkürzel finden Sie im Benutzerhandbuch.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="99"/>
        <source>Show frame type (I/P/B):</source>
        <translation>Bildtyp anzeigen (I/P/B):</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="112"/>
        <source>Overlay each frame&apos;s picture type (I, P or B) in the top-left corner of the thumbnail strip and/or the preview.</source>
        <translation>Blendet den Bildtyp (I, P oder B) jedes Frames in der oberen linken Ecke der Miniaturansicht und/oder der Vorschau ein.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="117"/>
        <source>Theme:</source>
        <translation>Design:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="130"/>
        <source>Follow the desktop&apos;s own colours, or pin a Light or Dark look for Snipwright. The editor&apos;s timeline and thumbnail bars stay dark in every theme. The change applies straight away.</source>
        <translation>Folgt den Farben des Desktops oder legt ein helles oder dunkles Erscheinungsbild für Snipwright fest. Die Zeitleiste und die Miniaturansichten des Editors bleiben in jedem Design dunkel. Die Änderung wird sofort angewendet.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="136"/>
        <source>Language:</source>
        <translation>Sprache:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="151"/>
        <source>The interface language. English is built in; other languages appear here once their translation file is added to the translations folder. Takes effect after a restart.</source>
        <translation>Die Benutzeroberflächensprache. Englisch ist standardmäßig integriert; andere Sprachen erscheinen hier, sobald ihre Übersetzungsdatei dem Ordner „translations“ hinzugefügt wurde. Wird nach einem Neustart wirksam.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="156"/>
        <source>Restore default window size</source>
        <translation>Standardfenstergröße wiederherstellen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="159"/>
        <source>Un-maximise and reset the window to its default size.</source>
        <translation>Maximierung aufheben und das Fenster auf seine Standardgröße zurücksetzen.</translation>
    </message>
</context>
<context>
    <name>GoToTimecodeDialog</name>
    <message>
        <location filename="../ui/goto_dialog.py" line="35"/>
        <source>Go to timecode</source>
        <translation>Gehe zu Timecode</translation>
    </message>
    <message>
        <location filename="../ui/goto_dialog.py" line="43"/>
        <source>Enter a timecode:</source>
        <translation>Timecode eingeben:</translation>
    </message>
    <message>
        <location filename="../ui/goto_dialog.py" line="53"/>
        <source>Precede with + or - for a relative jump</source>
        <translation>Mit + oder - davor für einen relativen Sprung</translation>
    </message>
    <message>
        <location filename="../ui/goto_dialog.py" line="106"/>
        <source>That isn&apos;t a valid timecode.</source>
        <translation>Das ist kein gültiger Timecode.</translation>
    </message>
</context>
<context>
    <name>IgnoreListDialog</name>
    <message>
        <location filename="../watch/tray.py" line="345"/>
        <source>Edit ignore list</source>
        <translation>Ignorierliste bearbeiten</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="351"/>
        <source>One programme title per line. Matching ignores case, and lines starting with # are comments.</source>
        <translation>Ein Sendungstitel pro Zeile. Groß- und Kleinschreibung spielt keine Rolle, Zeilen mit # am Anfang sind Kommentare.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="360"/>
        <source>Programme name</source>
        <translation>Sendungsname</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="361"/>
        <source>Keyword</source>
        <translation>Stichwort</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="363"/>
        <source>&lt;b&gt;Programme name&lt;/b&gt; - the file name must start with the entry.&lt;br&gt;&lt;b&gt;Keyword&lt;/b&gt; - the entry may appear anywhere in the name.&lt;br&gt;&lt;br&gt;An entry beginning with * is always matched anywhere.</source>
        <translation>&lt;b&gt;Sendungsname&lt;/b&gt; – der Dateiname muss mit dem Eintrag beginnen.&lt;br&gt;&lt;b&gt;Stichwort&lt;/b&gt; – der Eintrag darf an beliebiger Stelle im Namen stehen.&lt;br&gt;&lt;br&gt;Ein Eintrag, der mit * beginnt, wird immer an beliebiger Stelle abgeglichen.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="370"/>
        <source>Match:</source>
        <translation>Abgleich:</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="379"/>
        <source>Housekeeping</source>
        <translation>Aufräumen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="382"/>
        <source>Remove entries that haven&apos;t been seen for:</source>
        <translation>Einträge entfernen, die länger nicht mehr aufgetaucht sind als:</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="385"/>
        <source>After each complete scan, drop titles that no new recording has matched for this long — handy when a list built up over years is full of programmes that finished.</source>
        <translation>Entfernt nach jedem vollständigen Scan die Titel, auf die so lange keine neue Aufnahme mehr gepasst hat — praktisch, wenn eine über Jahre gewachsene Liste voller beendeter Sendungen ist.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="395"/>
        <source> months</source>
        <translation> Monate</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="397"/>
        <source>Most series return within a year, so 12 months is a safe starting point.</source>
        <translation>Die meisten Serien kehren innerhalb eines Jahres zurück, daher sind 12 Monate ein sicherer Ausgangswert.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="402"/>
        <source>Review and prune now…</source>
        <translation>Jetzt prüfen und aufräumen…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="404"/>
        <source>See when each title was last seen, and choose which to remove.</source>
        <translation>Zeigt an, wann jeder Titel zuletzt aufgetaucht ist, und lässt Sie auswählen, welche entfernt werden.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="413"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="416"/>
        <source>Save</source>
        <translation>Speichern</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="447"/>
        <source>Ignore list</source>
        <translation>Ignorierliste</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="448"/>
        <source>Couldn&apos;t save the ignore list:

%s</source>
        <translation>Die Ignorierliste konnte nicht gespeichert werden:

%s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="457"/>
        <source>Prune ignore list</source>
        <translation>Ignorierliste aufräumen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="458"/>
        <source>A scan is running. Wait for it to finish, then try again.</source>
        <translation>Es läuft gerade ein Scan. Warten Sie, bis er abgeschlossen ist, und versuchen Sie es dann erneut.</translation>
    </message>
</context>
<context>
    <name>IgnorePruneDialog</name>
    <message>
        <location filename="../watch/tray.py" line="183"/>
        <location filename="../watch/tray.py" line="296"/>
        <location filename="../watch/tray.py" line="305"/>
        <location filename="../watch/tray.py" line="331"/>
        <source>Prune ignore list</source>
        <translation>Ignorierliste aufräumen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="195"/>
        <source>&quot;Last seen&quot; is the date of the most recent recording that matched each title. Entries older than the chosen period are ticked ready to remove — untick anything you want to keep.</source>
        <translation>„Zuletzt gesehen“ ist das Datum der neuesten Aufnahme, die auf den jeweiligen Titel gepasst hat. Einträge, die älter als der gewählte Zeitraum sind, sind zum Entfernen angehakt — entfernen Sie das Häkchen bei allem, was Sie behalten möchten.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="204"/>
        <source>Programme</source>
        <translation>Sendung</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="204"/>
        <source>Last seen</source>
        <translation>Zuletzt gesehen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="204"/>
        <source>Months</source>
        <translation>Monate</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="220"/>
        <source>Tick all</source>
        <translation>Alle anhaken</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="223"/>
        <source>Tick none</source>
        <translation>Keine anhaken</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="227"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="230"/>
        <source>Remove ticked</source>
        <translation>Angehakte entfernen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="269"/>
        <source>The ignore list is empty.</source>
        <translation>Die Ignorierliste ist leer.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="272"/>
        <source>%d entries, %d not seen for %d months or more.</source>
        <translation>%d Einträge, davon %d seit %d Monaten oder länger nicht mehr gesehen.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="297"/>
        <source>Nothing is ticked, so there&apos;s nothing to remove.</source>
        <translation>Es ist nichts angehakt, es gibt also nichts zu entfernen.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="303"/>
        <source>…and %d more</source>
        <translation>…und %d weitere</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="306"/>
        <source>Remove %d entry/entries from the ignore list?

%s

Recordings already in your watched folders that matched these titles are marked as done, so removing them here won&apos;t send a back-catalogue through Comskip. New recordings will be picked up as normal.</source>
        <translation>%d Eintrag/Einträge aus der Ignorierliste entfernen?

%s

Aufnahmen in Ihren überwachten Ordnern, die auf diese Titel gepasst haben, werden als erledigt markiert. Durch das Entfernen wird also kein Altbestand durch Comskip geschickt. Neue Aufnahmen werden wie gewohnt verarbeitet.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="332"/>
        <source>Removed %d entry/entries. %d existing recording(s) were marked as already done.</source>
        <translation>%d Eintrag/Einträge entfernt. %d vorhandene Aufnahme(n) wurden als bereits erledigt markiert.</translation>
    </message>
</context>
<context>
    <name>InfoPanel</name>
    <message>
        <location filename="../ui/info_panel.py" line="55"/>
        <source>Info</source>
        <translation>Info</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="135"/>
        <source>Time</source>
        <translation>Zeit</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="143"/>
        <source>MB</source>
        <translation>MB</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="158"/>
        <source>Cursor</source>
        <translation>Cursor</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="159"/>
        <source>Program</source>
        <translation>Programm</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="160"/>
        <source>Selection</source>
        <translation>Auswahl</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="161"/>
        <source>Output</source>
        <translation>Ausgabe</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="162"/>
        <source>Joiner</source>
        <translation>Joiner</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="175"/>
        <location filename="../ui/info_panel.py" line="372"/>
        <location filename="../ui/info_panel.py" line="391"/>
        <source>--:--:--.--</source>
        <translation>--:--:--.--</translation>
    </message>
    <message>
        <location filename="../ui/info_panel.py" line="183"/>
        <location filename="../ui/info_panel.py" line="373"/>
        <location filename="../ui/info_panel.py" line="392"/>
        <source>0.00</source>
        <translation>0.00</translation>
    </message>
</context>
<context>
    <name>JoinerDialog</name>
    <message>
        <location filename="../ui/joiner_dialog.py" line="199"/>
        <source>Joiner editing</source>
        <translation>Joiner-Bearbeitung</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="218"/>
        <source>Load Joiner List…</source>
        <translation>Joiner-Liste laden…</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="219"/>
        <location filename="../ui/joiner_dialog.py" line="556"/>
        <location filename="../ui/joiner_dialog.py" line="570"/>
        <source>Save Joiner List</source>
        <translation>Joiner-Liste speichern</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="220"/>
        <source>Save Joiner List As…</source>
        <translation>Joiner-Liste speichern unter…</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="242"/>
        <source>Up</source>
        <translation>Nach oben</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="244"/>
        <source>Down</source>
        <translation>Nach unten</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="246"/>
        <source>Remove</source>
        <translation>Entfernen</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="229"/>
        <location filename="../ui/joiner_dialog.py" line="248"/>
        <location filename="../ui/joiner_dialog.py" line="420"/>
        <source>Description</source>
        <translation>Beschreibung</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="217"/>
        <source>File</source>
        <translation>Datei</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="229"/>
        <source>Filename</source>
        <translation>Dateiname</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="229"/>
        <source>Duration</source>
        <translation>Dauer</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="250"/>
        <source>Edit selection</source>
        <translation>Auswahl bearbeiten</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="252"/>
        <source>Add title</source>
        <translation>Titel hinzufügen</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="263"/>
        <source>Display full path name</source>
        <translation>Vollständigen Pfad anzeigen</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="265"/>
        <source>Clear after successful save/queue</source>
        <translation>Nach erfolgreichem Speichern/Einreihen leeren</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="275"/>
        <source>Fade to/from black (selected clip)</source>
        <translation>Ein-/Ausblenden aus Schwarz (ausgewählter Clip)</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="278"/>
        <source>In:</source>
        <translation>Anfang:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="288"/>
        <source>Out:</source>
        <translation>Ende:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="302"/>
        <location filename="../ui/joiner_dialog.py" line="500"/>
        <source>Clear all</source>
        <translation>Alles löschen</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="304"/>
        <source>Create video from joiner list…</source>
        <translation>Video aus Joiner-Liste erstellen…</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="311"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="314"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="359"/>
        <source>File not found: %s</source>
        <translation>Datei nicht gefunden: %s</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="420"/>
        <source>Description:</source>
        <translation>Beschreibung:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="481"/>
        <location filename="../ui/joiner_dialog.py" line="491"/>
        <source>Joiner</source>
        <translation>Joiner</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="481"/>
        <location filename="../ui/joiner_dialog.py" line="491"/>
        <source>The joiner list is empty.</source>
        <translation>Die Joiner-Liste ist leer.</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="501"/>
        <source>Remove all entries from the joiner list?</source>
        <translation>Alle Einträge aus der Joiner-Liste entfernen?</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="518"/>
        <location filename="../ui/joiner_dialog.py" line="527"/>
        <location filename="../ui/joiner_dialog.py" line="543"/>
        <source>Load Joiner List</source>
        <translation>Joiner-Liste laden</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="519"/>
        <location filename="../ui/joiner_dialog.py" line="557"/>
        <source>Joiner list (*%s);;All files (*)</source>
        <translation>Joiner-Liste (*%s);;Alle Dateien (*)</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="528"/>
        <source>Add the loaded entries to the current list?

Yes = append,  No = replace the current list.</source>
        <translation>Die geladenen Einträge zur aktuellen Liste hinzufügen?

Ja = anhängen,  Nein = aktuelle Liste ersetzen.</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="544"/>
        <source>Could not load the joiner list:

%s</source>
        <translation>Die Joiner-Liste konnte nicht geladen werden:

%s</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="571"/>
        <source>Could not save the joiner list:

%s</source>
        <translation>Die Joiner-Liste konnte nicht gespeichert werden:

%s</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="306"/>
        <source>Queue to batch</source>
        <translation>Zur Stapelverarbeitung</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="308"/>
        <source>Add this list to the batch queue, to be joined later with the Batch Manager&apos;s profile and output folder.</source>
        <translation>Diese Liste in die Warteschlange der Stapelverarbeitung stellen, um sie später mit dem Profil und Ausgabeordner des Batch-Managers zusammenzufügen.</translation>
    </message>
</context>
<context>
    <name>LoggingPage</name>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="25"/>
        <source>Number of log files to keep:</source>
        <translation>Anzahl der aufzubewahrenden Protokolldateien:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="31"/>
        <source>The oldest of the editor&apos;s log files beyond this many are deleted at startup. Set to 0 to keep every log.</source>
        <translation>Die ältesten Protokolldateien des Editors, die diese Anzahl überschreiten, werden beim Start gelöscht. Auf 0 setzen, um alle Protokolle zu behalten.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="38"/>
        <source>Where the editor writes its per-day log files, and how many it keeps. The Watcher is a separate application and keeps its own logs - set those in the Watcher&apos;s own settings window.</source>
        <translation>Gibt an, wohin der Editor seine täglichen Protokolldateien schreibt und wie viele er behält. Der Watcher ist eine separate Anwendung und führt eigene Protokolle – richten Sie diese im eigenen Einstellungsfenster des Watchers ein.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="43"/>
        <source>Verbose logging</source>
        <translation>Ausführliche Protokollierung</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="47"/>
        <source>Record extra detail in the log: export diagnostics (including the cutter&apos;s own output), plus playback and scene-selection activity. Useful for chasing problems; off by default, because those last two write a line every time you press play or click a scene.</source>
        <translation>Zeichnet zusätzliche Details im Protokoll auf: Exportdiagnosen (einschließlich der eigenen Ausgabe des Cutters) sowie Aktivitäten bei Wiedergabe und Szenenauswahl. Nützlich zur Fehlersuche; standardmäßig deaktiviert, da die beiden letztgenannten bei jedem Start der Wiedergabe und jedem Klick auf eine Szene eine Zeile schreiben.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="18"/>
        <source>Log files:</source>
        <translation>Protokolldateien:</translation>
    </message>
</context>
<context>
    <name>LogoStoreDialog</name>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="231"/>
        <location filename="../ui/logo_store_dialog.py" line="656"/>
        <location filename="../ui/logo_store_dialog.py" line="785"/>
        <location filename="../ui/logo_store_dialog.py" line="812"/>
        <location filename="../ui/logo_store_dialog.py" line="839"/>
        <location filename="../ui/logo_store_dialog.py" line="954"/>
        <source>Remembered logos</source>
        <translation>Gemerkte Logos</translation>
    </message>
    <message>
        <source>Chalkline learns each channel&apos;s logo when you correct a detection and save the project. A recorder that keeps the channel name gives a name here; one that keeps the service number gives a number. They are the same channel, but Snipwright cannot tell - fill in the missing half of a row and the logo will be used for recordings from both.</source>
        <translation type="vanished">Chalkline lernt das Logo eines Senders, wenn Sie eine Erkennung korrigieren und das Projekt speichern. Ein Aufnahmegerät, das den Sendernamen speichert, liefert hier einen Namen; eines, das die Dienstnummer speichert, liefert eine Nummer. Es ist derselbe Sender, doch Snipwright kann das nicht erkennen – ergänzen Sie die fehlende Hälfte einer Zeile, und das Logo wird für Aufnahmen aus beiden Quellen verwendet.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="275"/>
        <source>Logo</source>
        <translation>Logo</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="275"/>
        <source>Channel</source>
        <translation>Sender</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="275"/>
        <source>Service ID</source>
        <translation>Dienst-ID</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="276"/>
        <source>Mask</source>
        <translation>Maske</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="276"/>
        <source>Contrast</source>
        <translation>Kontrast</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="291"/>
        <source>Forget</source>
        <translation>Verwerfen</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="381"/>
        <source>Chalkline learned a logo while this window was open, and it has been added to the list: %s</source>
        <translation>Chalkline hat ein Logo gelernt, während dieses Fenster geöffnet war; es wurde der Liste hinzugefügt: %s</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="417"/>
        <source>%(count)dpx %(kind)s</source>
        <translation>%(count)dpx %(kind)s</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="420"/>
        <source>%(logo)s, best of %(held)d</source>
        <translation>%(logo)s, bestes von %(held)d</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="430"/>
        <source>%(count)dpx: %(seen)d project(s), %(false)d invented break(s)</source>
        <translation>%(count)dpx: %(seen)d Projekt(e), %(false)d erfundene Unterbrechung(en)</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="438"/>
        <source> - in use</source>
        <translation> – in Verwendung</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="466"/>
        <source>Nothing learned yet. Correct a detection and save the project, and the channel&apos;s logo will appear here.</source>
        <translation>Noch nichts gelernt. Korrigieren Sie eine Erkennung und speichern Sie das Projekt, dann erscheint das Logo des Senders hier.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="624"/>
        <source>A logo needs at least one of Channel or Service ID. Use Forget to remove it entirely.</source>
        <translation>Ein Logo braucht mindestens einen Eintrag unter Sender oder Dienst-ID. Verwenden Sie „Verwerfen“, um es vollständig zu entfernen.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="658"/>
        <source>“%s” already has a logo of its own. Joining them keeps both logos under the one name, and Snipwright uses whichever does better on the projects you correct.

Join them?</source>
        <translation>„%s“ hat bereits ein eigenes Logo. Beim Zusammenführen bleiben beide Logos unter einem Namen erhalten, und Snipwright verwendet dasjenige, das sich bei Ihren korrigierten Projekten besser bewährt.

Zusammenführen?</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="710"/>
        <source>The entries could not be joined - the list had changed. Try again.</source>
        <translation>Die Einträge konnten nicht zusammengeführt werden – die Liste hatte sich geändert. Versuchen Sie es erneut.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="741"/>
        <source>Joined into one entry holding %(held)d logo(s), using the %(use)dpx one for now. Correct a detection on this channel and save it, and the better logo will be chosen on the evidence.</source>
        <translation>Zu einem Eintrag mit %(held)d Logo(s) zusammengeführt; vorerst wird das %(use)dpx-Logo verwendet. Korrigieren Sie eine Erkennung bei diesem Sender und speichern Sie sie, dann wird das bessere Logo anhand der Belege gewählt.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="586"/>
        <location filename="../ui/logo_store_dialog.py" line="851"/>
        <location filename="../ui/logo_store_dialog.py" line="872"/>
        <source>this channel</source>
        <translation>dieser Sender</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="854"/>
        <source>Forget logo</source>
        <translation>Logo verwerfen</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="856"/>
        <source>Forget the logo remembered for “%s”?

Chalkline will learn it again the next time you correct a detection for that channel and save the project.</source>
        <translation>Das für „%s“ gemerkte Logo verwerfen?

Chalkline lernt es erneut, sobald Sie das nächste Mal eine Erkennung für diesen Sender korrigieren und das Projekt speichern.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="867"/>
        <location filename="../ui/logo_store_dialog.py" line="889"/>
        <source>Forgotten: %s</source>
        <translation>Verworfen: %s</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="955"/>
        <source>The logo list could not be saved:

%s</source>
        <translation>Die Logo-Liste konnte nicht gespeichert werden:

%s</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="276"/>
        <source>Idents</source>
        <translation>Idents</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="277"/>
        <source>Learn</source>
        <translation>Lernen</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="487"/>
        <source>Learn from the projects you correct on this channel. Untick it once the channel detects well: what it has learned is still used, and saving a correction no longer starts a learning pass.</source>
        <translation>Aus den Projekten lernen, die Sie bei diesem Sender korrigieren. Entfernen Sie das Häkchen, sobald der Sender gut erkannt wird: Was er gelernt hat, wird weiterhin verwendet, und das Speichern einer Korrektur startet keinen Lerndurchgang mehr.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="506"/>
        <source>No logo - this channel is recognised by the ident at the edges of its breaks. The picture is the most recent one learned.</source>
        <translation>Kein Logo – dieser Sender wird am Ident an den Rändern seiner Unterbrechungen erkannt. Das Bild zeigt das zuletzt gelernte.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="509"/>
        <source>No logo</source>
        <translation>Kein Logo</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="589"/>
        <source>%s will learn from the projects you correct again.</source>
        <translation>%s lernt wieder aus den Projekten, die Sie korrigieren.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="593"/>
        <source>%s will no longer learn from your corrections. What it has learned is still used to find its breaks.</source>
        <translation>%s lernt nicht mehr aus Ihren Korrekturen. Was er gelernt hat, wird weiterhin verwendet, um seine Unterbrechungen zu finden.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="258"/>
        <source>Chalkline learns each channel&apos;s logo, and any ident it shows at the edges of its breaks, when you correct a detection and save the project. A recorder that keeps the channel name gives a name here; one that keeps the service number gives a number. They are the same channel, but Snipwright cannot tell - fill in the missing half of a row and what was learned will be used for recordings from both. Untick Learn for a channel that already detects well: what it has learned is still used, but correcting it no longer spends minutes learning again.</source>
        <translation>Chalkline lernt das Logo eines Senders – und ein Ident, das er an den Rändern seiner Unterbrechungen zeigt –, wenn Sie eine Erkennung korrigieren und das Projekt speichern. Ein Aufnahmegerät, das den Sendernamen speichert, liefert hier einen Namen; eines, das die Dienstnummer speichert, liefert eine Nummer. Es ist derselbe Sender, doch Snipwright kann das nicht erkennen – ergänzen Sie die fehlende Hälfte einer Zeile, und das Gelernte wird für Aufnahmen aus beiden Quellen verwendet. Entfernen Sie das Häkchen bei „Lernen“ für einen Sender, der bereits gut erkannt wird: Was er gelernt hat, wird weiterhin verwendet, aber eine Korrektur löst kein minutenlanges erneutes Lernen mehr aus.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="770"/>
        <source>A channel needs at least one of Channel or Service ID. Use Forget to remove it entirely.</source>
        <translation>Ein Sender braucht mindestens einen Eintrag unter Sender oder Dienst-ID. Verwenden Sie „Verwerfen“, um ihn vollständig zu entfernen.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="787"/>
        <source>“%s” has a remembered logo. Joining them makes this channel&apos;s idents part of that channel, so both are used together.

Join them?</source>
        <translation>„%s“ hat ein gemerktes Logo. Beim Zusammenführen werden die Idents dieses Senders Teil jenes Senders, sodass beides gemeinsam verwendet wird.

Zusammenführen?</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="803"/>
        <source>Joined: %s now uses this channel&apos;s idents with its logo.</source>
        <translation>Zusammengeführt: %s verwendet die Idents dieses Senders nun zusammen mit seinem Logo.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="814"/>
        <source>“%s” already has idents of its own. Joining them keeps all of them under the one channel.

Join them?</source>
        <translation>„%s“ hat bereits eigene Idents. Beim Zusammenführen bleiben alle unter dem einen Sender erhalten.

Zusammenführen?</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="831"/>
        <source>Joined into one channel holding %d ident(s).</source>
        <translation>Zu einem Sender mit %d Ident(s) zusammengeführt.</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="875"/>
        <source>Forget idents</source>
        <translation>Idents verwerfen</translation>
    </message>
    <message>
        <location filename="../ui/logo_store_dialog.py" line="877"/>
        <source>Forget the idents remembered for “%s”?

Chalkline will learn them again the next time you correct a detection for that channel and save the project.</source>
        <translation>Die für „%s“ gemerkten Idents verwerfen?

Chalkline lernt sie erneut, sobald Sie das nächste Mal eine Erkennung für diesen Sender korrigieren und das Projekt speichern.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../main.py" line="621"/>
        <location filename="../main.py" line="822"/>
        <source>Remove Selected Scenes</source>
        <translation>Ausgewählte Szenen entfernen</translation>
    </message>
    <message>
        <location filename="../main.py" line="821"/>
        <source>Remove Selected Cuts</source>
        <translation>Ausgewählte Schnitte entfernen</translation>
    </message>
    <message>
        <location filename="../main.py" line="913"/>
        <source>You have unsaved changes to the scene list.

Save them as a project before continuing?</source>
        <translation>Sie haben ungespeicherte Änderungen an der Szenenliste.

Möchten Sie diese vor dem Fortfahren als Projekt speichern?</translation>
    </message>
    <message>
        <location filename="../main.py" line="934"/>
        <source>File</source>
        <translation>Datei</translation>
    </message>
    <message>
        <location filename="../main.py" line="939"/>
        <location filename="../main.py" line="3615"/>
        <location filename="../main.py" line="3773"/>
        <source>Open Video</source>
        <translation>Video öffnen</translation>
    </message>
    <message>
        <location filename="../main.py" line="943"/>
        <source>Open Recent</source>
        <translation>Zuletzt geöffnet</translation>
    </message>
    <message>
        <location filename="../main.py" line="950"/>
        <source>Save Video…</source>
        <translation>Video speichern…</translation>
    </message>
    <message>
        <location filename="../main.py" line="955"/>
        <source>Close Video</source>
        <translation>Video schließen</translation>
    </message>
    <message>
        <location filename="../main.py" line="962"/>
        <source>Open Project…</source>
        <translation>Projekt öffnen…</translation>
    </message>
    <message>
        <location filename="../main.py" line="967"/>
        <source>Save Project</source>
        <translation>Projekt speichern</translation>
    </message>
    <message>
        <location filename="../main.py" line="972"/>
        <source>Save Project As…</source>
        <translation>Projekt speichern unter…</translation>
    </message>
    <message>
        <location filename="../main.py" line="979"/>
        <location filename="../main.py" line="1807"/>
        <location filename="../main.py" line="4341"/>
        <location filename="../main.py" line="4364"/>
        <location filename="../main.py" line="4389"/>
        <location filename="../main.py" line="4397"/>
        <location filename="../main.py" line="4418"/>
        <source>Queue to Batch</source>
        <translation>Zur Stapelverarbeitung</translation>
    </message>
    <message>
        <location filename="../main.py" line="985"/>
        <source>Exit</source>
        <translation>Beenden</translation>
    </message>
    <message>
        <location filename="../main.py" line="991"/>
        <source>Edit</source>
        <translation>Bearbeiten</translation>
    </message>
    <message>
        <location filename="../main.py" line="996"/>
        <source>Mark In</source>
        <translation>Anfang markieren</translation>
    </message>
    <message>
        <location filename="../main.py" line="1001"/>
        <source>Mark Out</source>
        <translation>Ende markieren</translation>
    </message>
    <message>
        <location filename="../main.py" line="1008"/>
        <source>Add Selection</source>
        <translation>Auswahl hinzufügen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1013"/>
        <source>Add Unselected</source>
        <translation>Nicht ausgewählte hinzufügen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1018"/>
        <source>Cut Selection</source>
        <translation>Auswahl herausschneiden</translation>
    </message>
    <message>
        <location filename="../main.py" line="1023"/>
        <source>Trim Unselected</source>
        <translation>Nicht Ausgewähltes entfernen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1028"/>
        <source>Select All</source>
        <translation>Alles auswählen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1033"/>
        <source>Clear All Scenes</source>
        <translation>Alle Szenen löschen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1040"/>
        <source>Previous Scene Start</source>
        <translation>Vorheriger Szenenanfang</translation>
    </message>
    <message>
        <location filename="../main.py" line="1045"/>
        <source>Next Scene End</source>
        <translation>Nächstes Szenenende</translation>
    </message>
    <message>
        <location filename="../main.py" line="1052"/>
        <location filename="../main.py" line="1603"/>
        <location filename="../main.py" line="1636"/>
        <location filename="../main.py" line="1720"/>
        <location filename="../main.py" line="1731"/>
        <location filename="../main.py" line="1760"/>
        <location filename="../main.py" line="1930"/>
        <location filename="../main.py" line="2011"/>
        <source>Joiner</source>
        <translation>Joiner</translation>
    </message>
    <message>
        <location filename="../main.py" line="1057"/>
        <source>Add Current Project To Joiner List</source>
        <translation>Aktuelles Projekt zur Joiner-Liste hinzufügen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1062"/>
        <source>Edit Joiner List…</source>
        <translation>Joiner-Liste bearbeiten…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1067"/>
        <source>Create Video From Joiner List…</source>
        <translation>Video aus Joiner-Liste erstellen…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1079"/>
        <source>Tools</source>
        <translation>Werkzeuge</translation>
    </message>
    <message>
        <location filename="../main.py" line="1086"/>
        <source>Quick Stream Fix…</source>
        <translation>Schnelle Stream-Reparatur…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1097"/>
        <source>Detect Commercials…</source>
        <translation>Werbung erkennen…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1108"/>
        <source>Batch Manager…</source>
        <translation>Stapelverwaltung…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1119"/>
        <source>Manage Profiles…</source>
        <translation>Profile verwalten…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1133"/>
        <source>Show Video Programme Info</source>
        <translation>Programminformationen anzeigen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1146"/>
        <source>Trim and Copy Source File…</source>
        <translation>Quelldatei zuschneiden und kopieren…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1159"/>
        <source>Open Log Folder</source>
        <translation>Protokollordner öffnen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1170"/>
        <source>Settings…</source>
        <translation>Einstellungen…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1182"/>
        <source>Extras</source>
        <translation>Extras</translation>
    </message>
    <message>
        <location filename="../main.py" line="1184"/>
        <source>TV Renamer…</source>
        <translation>TV-Umbenenner…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1187"/>
        <source>Film Renamer…</source>
        <translation>Film-Umbenenner…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1190"/>
        <source>Launch Snipwright Watcher</source>
        <translation>Snipwright Watcher starten</translation>
    </message>
    <message>
        <location filename="../main.py" line="1197"/>
        <source>Help</source>
        <translation>Hilfe</translation>
    </message>
    <message>
        <location filename="../main.py" line="1199"/>
        <source>User Guide</source>
        <translation>Benutzerhandbuch</translation>
    </message>
    <message>
        <location filename="../main.py" line="1205"/>
        <source>Check for Updates…</source>
        <translation>Nach Updates suchen…</translation>
    </message>
    <message>
        <location filename="../main.py" line="1210"/>
        <location filename="../main.py" line="1381"/>
        <source>About %s</source>
        <translation>Über %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1304"/>
        <location filename="../main.py" line="1314"/>
        <source>Check for Updates</source>
        <translation>Nach Updates suchen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1305"/>
        <source>Couldn&apos;t reach GitHub to check for updates.

This is usually a network problem rather than anything wrong with Snipwright.</source>
        <translation>GitHub konnte für die Update-Prüfung nicht erreicht werden.

Das liegt meist am Netzwerk und nicht an Snipwright.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1315"/>
        <source>You&apos;re running the latest version (%s).</source>
        <translation>Sie verwenden bereits die neueste Version (%s).</translation>
    </message>
    <message>
        <location filename="../main.py" line="1324"/>
        <source>Update available</source>
        <translation>Update verfügbar</translation>
    </message>
    <message>
        <location filename="../main.py" line="1325"/>
        <source>Snipwright %s is available. You have %s.</source>
        <translation>Snipwright %s ist verfügbar. Sie haben %s.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1328"/>
        <source>Snipwright doesn&apos;t update itself - open the releases page to download it, then extract over your existing folder.</source>
        <translation>Snipwright aktualisiert sich nicht selbst – öffnen Sie die Releases-Seite, laden Sie die neue Version herunter und entpacken Sie sie über Ihren vorhandenen Ordner.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1331"/>
        <source>Open releases page</source>
        <translation>Releases-Seite öffnen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1336"/>
        <source>Skip this version</source>
        <translation>Diese Version überspringen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1390"/>
        <source>Version %s</source>
        <translation>Version %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1392"/>
        <source>An open-source, Linux-native, frame-accurate video cutter, heavily inspired by VideoReDo.</source>
        <translation>Ein quelloffener, Linux-nativer, bildgenauer Videoschnitt, stark inspiriert von VideoReDo.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1467"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../main.py" line="1512"/>
        <location filename="../main.py" line="1526"/>
        <location filename="../main.py" line="1541"/>
        <location filename="../main.py" line="1548"/>
        <source>Snipwright Watcher</source>
        <translation>Snipwright Watcher</translation>
    </message>
    <message>
        <location filename="../main.py" line="1513"/>
        <source>The Snipwright Watcher is already running - look for its icon in your system tray.</source>
        <translation>Der Snipwright Watcher läuft bereits – suchen Sie nach dem Symbol in Ihrer Systemleiste.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1527"/>
        <source>Couldn&apos;t find watcher.py alongside the application.</source>
        <translation>watcher.py konnte nicht neben der Anwendung gefunden werden.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1542"/>
        <source>Couldn&apos;t start the Watcher:
%s</source>
        <translation>Der Watcher konnte nicht gestartet werden:
%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1549"/>
        <source>The Snipwright Watcher has started and now lives in your system tray.</source>
        <translation>Der Snipwright Watcher wurde gestartet und befindet sich nun in Ihrer Systemleiste.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1604"/>
        <source>Open a recording before adding it to the joiner list.</source>
        <translation>Öffnen Sie eine Aufnahme, bevor Sie sie zur Joiner-Liste hinzufügen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1637"/>
        <source>The same %d scene%s from &quot;%s&quot; %s already in the joiner list.

Add again?</source>
        <translation>Dieselben %d Szene%s aus &quot;%s&quot; %s bereits in der Zusammenfüge-Liste.

Erneut hinzufügen?</translation>
    </message>
    <message>
        <location filename="../main.py" line="1647"/>
        <source>Already in the joiner list: %s</source>
        <translation>Bereits in der Zusammenfüge-Liste: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1721"/>
        <source>The joiner list is empty.  Add one or more scenes first (Joiner -&gt; Add Current Project To Joiner List).</source>
        <translation>Die Joiner-Liste ist leer. Fügen Sie zuerst eine oder mehrere Szenen hinzu (Joiner -&gt; Aktuelles Projekt zur Joiner-Liste hinzufügen).</translation>
    </message>
    <message>
        <location filename="../main.py" line="1732"/>
        <source>Some entries refer to files that can&apos;t be found, so the video can&apos;t be created:

%s</source>
        <translation>Einige Einträge verweisen auf Dateien, die nicht gefunden werden können, daher kann das Video nicht erstellt werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1761"/>
        <source>Because %s, the whole video will be re-encoded to a common format:%s

    H.264, %d×%d, %d fps, AAC stereo

Lower-resolution scenes are upscaled to match the highest. This re-encodes everything, so it&apos;s slower and slightly reduces quality.

Go ahead?</source>
        <translation>Aufgrund von %s wird das gesamte Video in ein gemeinsames Format neu kodiert:%s

    H.264, %d×%d, %d fps, AAC-Stereo

Szenen mit niedrigerer Auflösung werden hochskaliert, um der höchsten zu entsprechen. Dies kodiert alles neu, ist daher langsamer und verringert die Qualität geringfügig.

Fortfahren?</translation>
    </message>
    <message>
        <location filename="../main.py" line="1902"/>
        <source>Create Joined Video</source>
        <translation>Zusammengefügtes Video erstellen</translation>
    </message>
    <message>
        <location filename="../main.py" line="2869"/>
        <source>Learning %s&apos;s logo…</source>
        <translation>Logo von %s wird gelernt…</translation>
    </message>
    <message>
        <location filename="../main.py" line="2871"/>
        <source>Learning this channel&apos;s logo…</source>
        <translation>Logo dieses Senders wird gelernt…</translation>
    </message>
    <message>
        <location filename="../main.py" line="2873"/>
        <source> (%d waiting)</source>
        <translation> (%d in der Warteschlange)</translation>
    </message>
    <message>
        <location filename="../main.py" line="2876"/>
        <source>Chalkline is learning from the project you saved, so it can detect adverts on this channel more accurately next time. This runs in the background and takes a few minutes.</source>
        <translation>Chalkline lernt aus dem gespeicherten Projekt, um Werbung bei diesem Sender beim nächsten Mal genauer zu erkennen. Das läuft im Hintergrund und dauert einige Minuten.</translation>
    </message>
    <message>
        <location filename="../main.py" line="3987"/>
        <source>Indexing… %p%</source>
        <translation>Indizieren… %p%</translation>
    </message>
    <message>
        <location filename="../main.py" line="6028"/>
        <source>Settings</source>
        <translation>Einstellungen</translation>
    </message>
    <message>
        <location filename="../main.py" line="6031"/>
        <source>Settings brought across from your previous installation.</source>
        <translation>Einstellungen aus Ihrer vorherigen Installation übernommen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="6034"/>
        <source>Settings moved</source>
        <translation>Einstellungen verschoben</translation>
    </message>
    <message>
        <location filename="../main.py" line="6048"/>
        <source>Mark OUT for this scene - the OUT marker is still on the previous one.</source>
        <translation>OUT für diese Szene markieren - die OUT-Markierung steht noch auf der vorherigen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="6053"/>
        <source>Mark IN and OUT first, then add the scene.</source>
        <translation>Zuerst IN und OUT markieren, dann die Szene hinzufügen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="6107"/>
        <source>Mark OUT for this cut - the OUT marker is still on the previous one.</source>
        <translation>OUT für diesen Schnitt markieren - die OUT-Markierung steht noch auf dem vorherigen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="7118"/>
        <source>Export running</source>
        <translation>Export läuft</translation>
    </message>
    <message>
        <location filename="../main.py" line="7119"/>
        <source>An export is still being written in the background. Quitting will stop it, and the part-finished file will be discarded.

Quit anyway?</source>
        <translation>Im Hintergrund wird noch ein Export geschrieben. Beim Beenden wird er abgebrochen und die unfertige Datei verworfen.

Trotzdem beenden?</translation>
    </message>
    <message>
        <location filename="../main.py" line="2181"/>
        <location filename="../main.py" line="3902"/>
        <location filename="../main.py" line="4574"/>
        <location filename="../main.py" line="4698"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../main.py" line="1931"/>
        <source>Could not create the joined video:

%s</source>
        <translation>Das zusammengefügte Video konnte nicht erstellt werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2012"/>
        <source>That entry&apos;s file could no longer be found:

%s</source>
        <translation>Die Datei dieses Eintrags konnte nicht mehr gefunden werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2043"/>
        <source>Logs</source>
        <translation>Protokolle</translation>
    </message>
    <message>
        <location filename="../main.py" line="2044"/>
        <source>No log folder is available yet.</source>
        <translation>Es ist noch kein Protokollordner verfügbar.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2112"/>
        <location filename="../main.py" line="2149"/>
        <location filename="../main.py" line="2170"/>
        <location filename="../main.py" line="2186"/>
        <location filename="../main.py" line="2231"/>
        <location filename="../main.py" line="2247"/>
        <location filename="../main.py" line="2280"/>
        <source>Detect Commercials</source>
        <translation>Werbung erkennen</translation>
    </message>
    <message>
        <location filename="../main.py" line="2113"/>
        <location filename="../main.py" line="2623"/>
        <location filename="../main.py" line="4185"/>
        <location filename="../main.py" line="4389"/>
        <location filename="../main.py" line="4501"/>
        <source>Open a video first.</source>
        <translation>Öffnen Sie zuerst ein Video.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2294"/>
        <source>Import Project</source>
        <translation>Projekt importieren</translation>
    </message>
    <message>
        <location filename="../main.py" line="2499"/>
        <source>This project file could not be read:

%s</source>
        <translation>Diese Projektdatei konnte nicht gelesen werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2366"/>
        <location filename="../main.py" line="2509"/>
        <source>Locate video file</source>
        <translation>Videodatei suchen</translation>
    </message>
    <message>
        <location filename="../main.py" line="2511"/>
        <source>There was a problem opening the video file associated with this project.
The original file may not exist or may be mapped to a different drive or folder.

Original file: %s

Do you wish to manually search for the file?</source>
        <translation>Beim Öffnen der mit diesem Projekt verknüpften Videodatei ist ein Problem aufgetreten.
Die Originaldatei existiert möglicherweise nicht oder befindet sich auf einem anderen Laufwerk oder Ordner.

Originaldatei: %s

Möchten Sie manuell nach der Datei suchen?</translation>
    </message>
    <message>
        <location filename="../main.py" line="2536"/>
        <source>Locate video for project</source>
        <translation>Video für das Projekt suchen</translation>
    </message>
    <message>
        <location filename="../main.py" line="2629"/>
        <source>No scenes marked to keep. Mark at least one scene before saving a project.</source>
        <translation>Keine Szenen zum Behalten markiert. Markieren Sie mindestens eine Szene, bevor Sie ein Projekt speichern.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2653"/>
        <source>The project could not be saved:

%s</source>
        <translation>Das Projekt konnte nicht gespeichert werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="3076"/>
        <source>Save Project As</source>
        <translation>Projekt speichern unter</translation>
    </message>
    <message>
        <location filename="../main.py" line="3232"/>
        <source>Language changed</source>
        <translation>Sprache geändert</translation>
    </message>
    <message>
        <location filename="../main.py" line="3234"/>
        <source>The interface language will change when Snipwright is restarted.</source>
        <translation>Die Sprache der Benutzeroberfläche ändert sich beim Neustart von Snipwright.</translation>
    </message>
    <message>
        <location filename="../main.py" line="3236"/>
        <source>Restart now?</source>
        <translation>Jetzt neu starten?</translation>
    </message>
    <message>
        <location filename="../main.py" line="3238"/>
        <source>Restart now</source>
        <translation>Jetzt neu starten</translation>
    </message>
    <message>
        <location filename="../main.py" line="1333"/>
        <location filename="../main.py" line="3240"/>
        <source>Later</source>
        <translation>Später</translation>
    </message>
    <message>
        <location filename="../main.py" line="3677"/>
        <source>Open Multiple Files</source>
        <translation>Mehrere Dateien öffnen</translation>
    </message>
    <message>
        <location filename="../main.py" line="3678"/>
        <source>These files could not be read and were not added:</source>
        <translation>Diese Dateien konnten nicht gelesen werden und wurden nicht hinzugefügt:</translation>
    </message>
    <message>
        <location filename="../main.py" line="3706"/>
        <source>External tools</source>
        <translation>Externe Werkzeuge</translation>
    </message>
    <message>
        <location filename="../main.py" line="3707"/>
        <source>The preview works without them, but exporting, joining and showing stream info need ffmpeg and ffprobe.

</source>
        <translation>Die Vorschau funktioniert auch ohne sie, aber das Exportieren, Zusammenfügen und Anzeigen von Stream-Informationen erfordern ffmpeg und ffprobe.

</translation>
    </message>
    <message>
        <location filename="../main.py" line="3774"/>
        <source>That file no longer exists:
%s</source>
        <translation>Diese Datei existiert nicht mehr:
%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="3853"/>
        <source>(no recent files)</source>
        <translation>(keine zuletzt geöffneten Dateien)</translation>
    </message>
    <message>
        <location filename="../main.py" line="3875"/>
        <source>Clear Recent</source>
        <translation>Liste leeren</translation>
    </message>
    <message>
        <location filename="../main.py" line="3901"/>
        <source>Quick Stream Fix on open (remuxing)…</source>
        <translation>Schnelle Stream-Reparatur beim Öffnen (Remuxing)…</translation>
    </message>
    <message>
        <location filename="../main.py" line="3907"/>
        <source>Opening</source>
        <translation>Wird geöffnet</translation>
    </message>
    <message>
        <location filename="../main.py" line="3930"/>
        <source>Quick Stream Fix on open failed</source>
        <translation>Schnelle Stream-Reparatur beim Öffnen fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../main.py" line="3931"/>
        <source>%s

Opening the original file instead.</source>
        <translation>%s

Es wird stattdessen die Originaldatei geöffnet.</translation>
    </message>
    <message>
        <location filename="../main.py" line="3993"/>
        <source>Indexing video…</source>
        <translation>Video wird indiziert…</translation>
    </message>
    <message>
        <location filename="../main.py" line="4184"/>
        <location filename="../main.py" line="4198"/>
        <source>Export</source>
        <translation>Exportieren</translation>
    </message>
    <message>
        <location filename="../main.py" line="4199"/>
        <source>No segments marked to keep. Mark at least one green segment before exporting.</source>
        <translation>Keine Segmente zum Behalten markiert. Markieren Sie mindestens ein grünes Segment vor dem Exportieren.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1877"/>
        <location filename="../main.py" line="4252"/>
        <source>mkvmerge not found</source>
        <translation>mkvmerge nicht gefunden</translation>
    </message>
    <message>
        <location filename="../main.py" line="4253"/>
        <source>mkvmerge (mkvtoolnix) isn&apos;t installed or set in Settings.

MKV export still works and stays lossless, but the audio is stored in a less-portable wrapper rather than native AAC.  It plays in Plex/Jellyfin and other ffmpeg-based players.

Installing mkvtoolnix - or pointing Settings &gt; Paths at an mkvmerge - gives the portable, native-AAC result.

Export to MKV anyway?</source>
        <translation>mkvmerge (mkvtoolnix) ist nicht installiert oder in den Einstellungen festgelegt.

Der MKV-Export funktioniert weiterhin und bleibt verlustfrei, aber das Audio wird in einem weniger portablen Container statt in nativem AAC gespeichert. Es lässt sich in Plex/Jellyfin und anderen ffmpeg-basierten Playern abspielen.

Die Installation von mkvtoolnix – oder das Verweisen unter Einstellungen &gt; Pfade auf ein mkvmerge – liefert das portable, native AAC-Ergebnis.

Trotzdem als MKV exportieren?</translation>
    </message>
    <message>
        <location filename="../main.py" line="4398"/>
        <source>No segments marked to keep. Mark at least one green segment before queueing.</source>
        <translation>Keine Segmente zum Behalten markiert. Markieren Sie mindestens ein grünes Segment, bevor Sie es in die Warteschlange einreihen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4342"/>
        <source>Couldn&apos;t create the batch queue folder:

%s</source>
        <translation>Der Ordner für die Stapel-Warteschlange konnte nicht erstellt werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="4365"/>
        <source>The project couldn&apos;t be saved for batching:

%s</source>
        <translation>Das Projekt konnte nicht für die Stapelverarbeitung gespeichert werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="4419"/>
        <source>&quot;%s&quot; is already in the batch queue.

Add it again?</source>
        <translation>&quot;%s&quot; ist bereits in der Stapel-Warteschlange.

Erneut hinzufügen?</translation>
    </message>
    <message>
        <location filename="../main.py" line="4426"/>
        <source>Already in the batch queue: %s</source>
        <translation>Bereits in der Stapel-Warteschlange: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="4465"/>
        <source>Already Quick Stream Fixed</source>
        <translation>Bereits mit Schneller Stream-Reparatur verarbeitet</translation>
    </message>
    <message>
        <location filename="../main.py" line="4466"/>
        <source>This file appears to have already been processed by Quick Stream Fix.

Run Quick Stream Fix on it again anyway?</source>
        <translation>Diese Datei scheint bereits mit der Schnellen Stream-Reparatur verarbeitet worden zu sein.

Möchten Sie die Schnelle Stream-Reparatur trotzdem erneut ausführen?</translation>
    </message>
    <message>
        <location filename="../main.py" line="4500"/>
        <location filename="../main.py" line="4511"/>
        <location filename="../main.py" line="4579"/>
        <location filename="../main.py" line="4703"/>
        <source>Quick Stream Fix</source>
        <translation>Schnelle Stream-Reparatur</translation>
    </message>
    <message>
        <location filename="../main.py" line="4513"/>
        <source>How would you like to run Quick Stream Fix?</source>
        <translation>Wie möchten Sie die schnelle Stream-Reparatur ausführen?</translation>
    </message>
    <message>
        <location filename="../main.py" line="4515"/>
        <source>Repair and reload: repair to temporary storage and reload it now, carrying your current scene markers across (recommended when editing).

Repair and save a copy: write a permanently-fixed copy to a location you choose, without changing what&apos;s currently open.</source>
        <translation>Reparieren und neu laden: in den temporären Speicher reparieren und sofort neu laden, wobei Ihre aktuellen Szenenmarkierungen übernommen werden (beim Bearbeiten empfohlen).

Reparieren und Kopie speichern: eine dauerhaft reparierte Kopie an einem Ort Ihrer Wahl ablegen, ohne das aktuell Geöffnete zu verändern.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4522"/>
        <source>Repair and reload</source>
        <translation>Reparieren und neu laden</translation>
    </message>
    <message>
        <location filename="../main.py" line="4523"/>
        <source>Repair and save a copy…</source>
        <translation>Reparieren und Kopie speichern…</translation>
    </message>
    <message>
        <location filename="../main.py" line="4573"/>
        <location filename="../main.py" line="4697"/>
        <source>Repairing stream (remuxing)…</source>
        <translation>Stream wird repariert (Remuxing)…</translation>
    </message>
    <message>
        <location filename="../main.py" line="4592"/>
        <location filename="../main.py" line="5019"/>
        <source>Re-indexing repaired stream…</source>
        <translation>Reparierter Stream wird neu indiziert…</translation>
    </message>
    <message>
        <location filename="../main.py" line="4632"/>
        <source>Stream repaired and reloaded - check your scene markers.</source>
        <translation>Stream repariert und neu geladen - prüfen Sie Ihre Szenenmarkierungen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4637"/>
        <location filename="../main.py" line="5076"/>
        <source>Stream repaired</source>
        <translation>Stream repariert</translation>
    </message>
    <message>
        <location filename="../main.py" line="4638"/>
        <source>The stream has been repaired and reloaded.

Your scene markers have been carried over, but the repair can shift them slightly. Please check each scene (double-click a scene to jump to its start) and adjust if needed.</source>
        <translation>Der Stream wurde repariert und neu geladen.

Ihre Szenenmarker wurden übernommen, aber die Reparatur kann sie leicht verschieben. Bitte überprüfen Sie jede Szene (Doppelklick auf eine Szene, um zu deren Anfang zu springen) und passen Sie sie bei Bedarf an.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4646"/>
        <source>Stream repaired and reloaded.</source>
        <translation>Stream repariert und neu geladen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4657"/>
        <location filename="../main.py" line="4730"/>
        <source>Quick Stream Fix failed</source>
        <translation>Schnelle Stream-Reparatur fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../main.py" line="4688"/>
        <source>Quick Stream Fix - Save As</source>
        <translation>Schnelle Stream-Reparatur - Speichern unter</translation>
    </message>
    <message>
        <location filename="../main.py" line="4721"/>
        <source>Quick Stream Fix complete</source>
        <translation>Schnelle Stream-Reparatur abgeschlossen</translation>
    </message>
    <message>
        <location filename="../main.py" line="4722"/>
        <source>Saved:
%s</source>
        <translation>Gespeichert:
%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1878"/>
        <source>mkvmerge (mkvtoolnix) isn&apos;t installed or set in Settings.

MKV export will still work and stays lossless, but the audio is stored in a less-portable wrapper that some video players may reject, rather than native AAC.

Installing mkvtoolnix - or pointing Settings &gt; Paths at an mkvmerge - gives the portable, widely-compatible result.

Export to MKV anyway?</source>
        <translation>mkvmerge (mkvtoolnix) ist nicht installiert oder in den Einstellungen festgelegt.

Der MKV-Export funktioniert weiterhin und bleibt verlustfrei, aber das Audio wird in einem weniger portablen Container gespeichert, den einige Videoplayer möglicherweise ablehnen, statt in nativem AAC.

Die Installation von mkvtoolnix – oder das Verweisen unter Einstellungen &gt; Pfade auf ein mkvmerge – liefert das portable, weithin kompatible Ergebnis.

Trotzdem als MKV exportieren?</translation>
    </message>
    <message>
        <location filename="../main.py" line="4838"/>
        <source>Export produced no video</source>
        <translation>Export hat kein Video erzeugt</translation>
    </message>
    <message>
        <location filename="../main.py" line="4839"/>
        <source>The export contained no usable video, so it has not been saved. This normally means the recording itself is damaged - a signal dropout, or a capture that was interrupted.

Quick Stream Fix rebuilds the recording&apos;s timestamps without re-encoding, and usually recovers it. Would you like to run it on the source? The repaired file will be reloaded with your scene markers so you can check them before saving.</source>
        <translation>Der Export enthielt kein brauchbares Video und wurde daher nicht gespeichert. Das bedeutet normalerweise, dass die Aufnahme selbst beschädigt ist - ein Signalausfall oder eine unterbrochene Aufzeichnung.

Die Schnelle Stream-Reparatur erneuert die Zeitstempel der Aufnahme ohne Neukodierung und stellt sie meist wieder her. Möchten Sie sie auf der Quelle ausführen? Die reparierte Datei wird mit Ihren Szenenmarkern neu geladen, sodass Sie diese vor dem Speichern überprüfen können.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4859"/>
        <source>Export failed</source>
        <translation>Export fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../main.py" line="2000"/>
        <location filename="../main.py" line="4942"/>
        <source>Export moved to the Batch Manager - it carries on in the background. Tools → Batch Manager to watch it.</source>
        <translation>Export in den Batch-Manager verschoben – er läuft im Hintergrund weiter. Werkzeuge → Batch-Manager, um ihn zu verfolgen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="4999"/>
        <source>Repairing the stream (Quick Stream Fix)…</source>
        <translation>Der Stream wird repariert (schnelle Stream-Reparatur)…</translation>
    </message>
    <message>
        <location filename="../main.py" line="5005"/>
        <source>Repairing</source>
        <translation>Reparatur läuft</translation>
    </message>
    <message>
        <location filename="../main.py" line="5070"/>
        <source>Stream repaired and reloaded - check your scene markers, then Save Video.</source>
        <translation>Stream repariert und neu geladen - prüfen Sie Ihre Szenenmarkierungen und speichern Sie dann das Video.</translation>
    </message>
    <message>
        <location filename="../main.py" line="5077"/>
        <source>The stream has been repaired and reloaded.

Your scene markers have been carried over, but the repair can shift them slightly. Please check each scene (double-click a scene to jump to its start) and adjust if needed, then click Save Video when you&apos;re happy.</source>
        <translation>Der Stream wurde repariert und neu geladen.

Ihre Szenenmarker wurden übernommen, aber die Reparatur kann sie leicht verschieben. Bitte überprüfen Sie jede Szene (Doppelklick auf eine Szene, um zu deren Anfang zu springen), passen Sie sie bei Bedarf an und klicken Sie auf Video speichern, wenn Sie zufrieden sind.</translation>
    </message>
    <message>
        <location filename="../main.py" line="5092"/>
        <source>Repair failed</source>
        <translation>Reparatur fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../main.py" line="5093"/>
        <source>The stream could not be repaired automatically:

%s</source>
        <translation>Der Stream konnte nicht automatisch repariert werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="6088"/>
        <source>Mark IN and OUT first, then cut.</source>
        <translation>Zuerst IN und OUT markieren, dann schneiden.</translation>
    </message>
    <message>
        <location filename="../main.py" line="6160"/>
        <source>Mark IN and OUT first, then trim.</source>
        <translation>Zuerst IN und OUT markieren, dann zuschneiden.</translation>
    </message>
    <message>
        <location filename="../main.py" line="7099"/>
        <source>Batch running</source>
        <translation>Stapelverarbeitung läuft</translation>
    </message>
    <message>
        <location filename="../main.py" line="7100"/>
        <source>A batch is still running. Quitting will stop it after the current job.

Quit anyway?</source>
        <translation>Eine Stapelverarbeitung läuft noch. Das Beenden stoppt sie nach dem aktuellen Auftrag.

Trotzdem beenden?</translation>
    </message>
    <message>
        <location filename="../main.py" line="5329"/>
        <source>Loaded %s chapter mark(s) from the file.</source>
        <translation>%s Kapitelmarke(n) aus der Datei geladen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="1682"/>
        <source>Added %(count)d scene(s) from %(name)s (%(total)d in joiner list).</source>
        <translation>%(count)d Szene(n) aus %(name)s hinzugefügt (%(total)d in der Joiner-Liste).</translation>
    </message>
    <message>
        <location filename="../main.py" line="1915"/>
        <source>Joined video created: %s</source>
        <translation>Zusammengefügtes Video erstellt: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2150"/>
        <source>The Comskip program hasn&apos;t been set yet.

Add the path to Comskip (and optionally its .ini file) in Tools &gt; Settings &gt; Advert detection, or switch to Chalkline there - it is built in and needs no setup.</source>
        <translation>Das Comskip-Programm wurde noch nicht festgelegt.

Fügen Sie den Pfad zu Comskip (und optional der zugehörigen .ini-Datei) unter Werkzeuge &gt; Einstellungen &gt; Werbeerkennung hinzu, oder wechseln Sie dort zu Chalkline – es ist integriert und muss nicht eingerichtet werden.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2171"/>
        <source>This will replace your current scene markers with the detected scenes. Continue?</source>
        <translation>Dies ersetzt Ihre aktuellen Szenenmarker durch die erkannten Szenen. Fortfahren?</translation>
    </message>
    <message>
        <location filename="../main.py" line="2180"/>
        <source>Detecting commercials (%s)…</source>
        <translation>Werbung wird erkannt (%s)…</translation>
    </message>
    <message>
        <location filename="../main.py" line="2195"/>
        <location filename="../main.py" line="2216"/>
        <source>Detecting commercials (%s) - pass %s…</source>
        <translation>Werbung wird erkannt (%s) – Durchlauf %s…</translation>
    </message>
    <message>
        <location filename="../main.py" line="2232"/>
        <source>%s finished but its output could not be read:

%s</source>
        <translation>%s wurde beendet, aber die Ausgabe konnte nicht gelesen werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2248"/>
        <source>%s found no commercials to remove (the whole file is one scene).</source>
        <translation>%s hat keine zu entfernende Werbung gefunden (die gesamte Datei ist eine einzige Szene).</translation>
    </message>
    <message>
        <location filename="../main.py" line="2270"/>
        <source>%(detector)s found %(count)d scene(s).</source>
        <translation>%(detector)s hat %(count)d Szene(n) gefunden.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2345"/>
        <source>This EDL could not be read:

%s</source>
        <translation>Diese EDL konnte nicht gelesen werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2353"/>
        <source>This EDL contains no cut regions, so there is nothing to apply.</source>
        <translation>Diese EDL enthält keine Schnittbereiche, es gibt also nichts anzuwenden.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2368"/>
        <source>An EDL contains only a cut list, not a video.
It has to be applied to a recording that is already open.

EDL: %s

Do you wish to select the video it applies to?</source>
        <translation>Eine EDL enthält nur eine Schnittliste, kein Video.
Sie muss auf eine bereits geöffnete Aufnahme angewendet werden.

EDL: %s

Möchten Sie das Video auswählen, für das sie gilt?</translation>
    </message>
    <message>
        <location filename="../main.py" line="2389"/>
        <source>Locate video for EDL</source>
        <translation>Video für die EDL suchen</translation>
    </message>
    <message>
        <location filename="../main.py" line="2422"/>
        <source>This EDL runs %(over)s seconds past the end of the video.

It was probably made from a different recording. Apply it anyway?</source>
        <translation>Diese EDL reicht %(over)s Sekunden über das Ende des Videos hinaus.

Sie stammt wahrscheinlich von einer anderen Aufnahme. Trotzdem anwenden?</translation>
    </message>
    <message>
        <location filename="../main.py" line="2438"/>
        <source>This EDL could not be applied:

%s</source>
        <translation>Diese EDL konnte nicht angewendet werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2446"/>
        <source>This EDL removes the whole recording, so there would be nothing left to keep.</source>
        <translation>Diese EDL entfernt die gesamte Aufnahme, es bliebe also nichts übrig.</translation>
    </message>
    <message>
        <location filename="../main.py" line="2462"/>
        <source>EDL loaded: %(name)s - %(cuts)d cut regions to %(last).1fs of a %(duration).1fs video</source>
        <translation>EDL geladen: %(name)s – %(cuts)d Schnittbereiche bis %(last).1fs eines %(duration).1fs langen Videos</translation>
    </message>
    <message>
        <location filename="../main.py" line="2565"/>
        <source>Project loaded: %s</source>
        <translation>Projekt geladen: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2660"/>
        <location filename="../main.py" line="2702"/>
        <source>Project saved: %s</source>
        <translation>Projekt gespeichert: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="2983"/>
        <source>Chalkline found a better logo for %s from your edit - detection on this channel should improve.</source>
        <translation>Chalkline hat aus Ihrer Bearbeitung ein besseres Logo für %s gefunden – die Erkennung bei diesem Sender sollte sich verbessern.</translation>
    </message>
    <message>
        <location filename="../main.py" line="3004"/>
        <source>Chalkline learned %s&apos;s logo from your edit - detection on this channel should improve.</source>
        <translation>Chalkline hat das Logo von %s aus Ihrer Bearbeitung gelernt – die Erkennung bei diesem Sender sollte sich verbessern.</translation>
    </message>
    <message>
        <location filename="../main.py" line="3133"/>
        <source>An EDL stores cut times only, so the %(count)s marker(s) in this project will not be saved.

Continue?</source>
        <translation>Eine EDL speichert nur Schnittzeiten, daher werden die %(count)s Marker in diesem Projekt nicht gespeichert.

Fortfahren?</translation>
    </message>
    <message>
        <location filename="../main.py" line="3149"/>
        <source>The EDL could not be written:

%s</source>
        <translation>Die EDL konnte nicht geschrieben werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="3154"/>
        <source>EDL saved: %s</source>
        <translation>EDL gespeichert: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="3682"/>
        <source>Added %(count)d file(s) to the joiner list (%(total)d entries).</source>
        <translation>%(count)d Datei(en) zur Joiner-Liste hinzugefügt (%(total)d Einträge).</translation>
    </message>
    <message>
        <location filename="../main.py" line="1816"/>
        <location filename="../main.py" line="4439"/>
        <source>Queued to batch: %(name)s (%(profile)s). Open Tools → Batch Manager to run it.</source>
        <translation>Zur Stapelverarbeitung eingereiht: %(name)s (%(profile)s). Öffnen Sie Werkzeuge → Stapelverwaltung, um sie auszuführen.</translation>
    </message>
    <message>
        <location filename="../main.py" line="5460"/>
        <source>Could not open video: %s</source>
        <translation>Video konnte nicht geöffnet werden: %s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1072"/>
        <source>Queue Joiner List to Batch</source>
        <translation>Joiner-Liste zur Stapelverarbeitung</translation>
    </message>
    <message>
        <location filename="../main.py" line="1808"/>
        <location filename="../main.py" line="1978"/>
        <source>The joiner list could not be queued:

%s</source>
        <translation>Die Joiner-Liste konnte nicht eingereiht werden:

%s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1901"/>
        <source>Creating %s</source>
        <translation>%s wird erstellt</translation>
    </message>
    <message>
        <location filename="../main.py" line="1977"/>
        <source>Send to Batch</source>
        <translation>An Stapel senden</translation>
    </message>
    <message>
        <location filename="../main.py" line="1420"/>
        <source>System</source>
        <translation>System</translation>
    </message>
    <message>
        <location filename="../main.py" line="1421"/>
        <source>FFmpeg inside PyAV</source>
        <translation>FFmpeg in PyAV</translation>
    </message>
    <message>
        <location filename="../main.py" line="1422"/>
        <source>FFmpeg program</source>
        <translation>FFmpeg-Programm</translation>
    </message>
    <message>
        <location filename="../main.py" line="1429"/>
        <source>not found</source>
        <translation>nicht gefunden</translation>
    </message>
    <message>
        <location filename="../main.py" line="1433"/>
        <source>%(version)s - tested with %(tested)s</source>
        <translation>%(version)s – getestet mit %(tested)s</translation>
    </message>
    <message>
        <location filename="../main.py" line="1445"/>
        <source>Running on</source>
        <translation>Verwendete Komponenten</translation>
    </message>
    <message>
        <location filename="../main.py" line="1460"/>
        <source>Copy details</source>
        <translation>Details kopieren</translation>
    </message>
    <message>
        <location filename="../main.py" line="1464"/>
        <source>Copied</source>
        <translation>Kopiert</translation>
    </message>
</context>
<context>
    <name>MaintenancePage</name>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="23"/>
        <source>Quick Stream Fix working copies</source>
        <translation>Quick-Stream-Fix-Arbeitskopien</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="27"/>
        <source>Delete cached data older than</source>
        <translation>Gecachte Daten löschen, die älter sind als</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="36"/>
        <location filename="../ui/settings_pages/maintenance.py" line="57"/>
        <location filename="../ui/settings_pages/maintenance.py" line="165"/>
        <source>Delete now</source>
        <translation>Jetzt löschen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="41"/>
        <source>Cached frame indices and Quick Stream Fix records for files you haven&apos;t opened in this long are removed at startup. Set to 0 (never) to keep them indefinitely.</source>
        <translation>Gecachte Frame-Indizes und Datensätze der Schnellen Stream-Reparatur für Dateien, die Sie so lange nicht geöffnet haben, werden beim Start entfernt. Auf 0 (nie) setzen, um sie unbegrenzt zu behalten.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="49"/>
        <source>Delete remembered renamer matches older than</source>
        <translation>Gespeicherte Umbenennungs-Treffer löschen, die älter sind als</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="62"/>
        <source>The TV and film renamer remember each TMDB/IMDb match so they don&apos;t look it up again. These are kept in their own file; purge old ones here, or set to 0 (never) to keep them indefinitely.</source>
        <translation>Die Serien- und Film-Umbenennung merkt sich jeden TMDB/IMDb-Treffer, um ihn nicht erneut nachzuschlagen. Diese werden in einer eigenen Datei gespeichert; alte hier entfernen oder mit 0 (nie) dauerhaft behalten.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="68"/>
        <source>Edit config.json</source>
        <translation>config.json bearbeiten</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="75"/>
        <source>Edit every setting directly as text - including the keyboard shortcuts, which have no controls of their own here. Changes apply as soon as you save, and any clashing keys are flagged then.</source>
        <translation>Bearbeiten Sie jede Einstellung direkt als Text – einschließlich der Tastaturkürzel, für die es hier keine eigenen Bedienelemente gibt. Änderungen werden sofort nach dem Speichern wirksam, und eventuelle Tastenkonflikte werden dabei direkt markiert.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="81"/>
        <source>Restore Default Settings</source>
        <translation>Standardeinstellungen wiederherstellen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="88"/>
        <source>Reset every setting - paths, options and keyboard shortcuts - back to its default. Your recordings and projects aren&apos;t affected.</source>
        <translation>Setzt jede Einstellung – Pfade, Optionen und Tastaturkürzel – auf die Standardwerte zurück. Ihre Aufnahmen und Projekte sind davon nicht betroffen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="97"/>
        <source>Renamer cache cleared</source>
        <translation>Umbenennungs-Cache geleert</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="98"/>
        <source>The remembered renamer matches have been deleted.</source>
        <translation>Die gespeicherten Umbenennungs-Treffer wurden gelöscht.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="104"/>
        <source>Check for new versions:</source>
        <translation>Nach neuen Versionen suchen:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="106"/>
        <source>Never</source>
        <translation>Nie</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="107"/>
        <source>Daily</source>
        <translation>Täglich</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="108"/>
        <source>Weekly</source>
        <translation>Wöchentlich</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="109"/>
        <source>Monthly</source>
        <translation>Monatlich</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="115"/>
        <source>Check now</source>
        <translation>Jetzt prüfen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="120"/>
        <source>Asks GitHub whether a newer Snipwright has been released and tells you if there is one. Nothing is downloaded or installed - only the public list of releases is read. Set to Never to disable automatic checks; a manual check can always be made with the Check now button.</source>
        <translation>Fragt bei GitHub nach, ob eine neuere Version von Snipwright veröffentlicht wurde, und weist Sie darauf hin. Es wird nichts heruntergeladen oder installiert – gelesen wird nur die öffentliche Releases-Liste. Stellen Sie auf „Nie“, um die automatische Prüfung abzuschalten; eine manuelle Prüfung ist jederzeit über die Schaltfläche „Jetzt prüfen“ möglich.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="161"/>
        <source>Open folder</source>
        <translation>Ordner öffnen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="185"/>
        <source>Checked at startup. Anything still in use is never deleted - open in the editor, being exported, or referenced by a job in the batch queue.</source>
        <translation>Wird beim Start geprüft. Was noch in Gebrauch ist, wird nie gelöscht – im Editor geöffnet, gerade exportiert oder von einem Auftrag in der Batch-Warteschlange referenziert.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="225"/>
        <source>Delete %d working copy/copies, freeing %s?

Anything still in use is skipped - open in the editor, being exported, or needed by a queued batch job.</source>
        <translation>%d Arbeitskopie(n) löschen und damit %s freigeben?

Was noch in Gebrauch ist, wird übersprungen – im Editor geöffnet, gerade exportiert oder von einem eingereihten Batch-Auftrag benötigt.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="177"/>
        <source>Delete leftovers older than</source>
        <translation>Reste löschen, die älter sind als</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="30"/>
        <location filename="../ui/settings_pages/maintenance.py" line="52"/>
        <location filename="../ui/settings_pages/maintenance.py" line="180"/>
        <source> days</source>
        <translation> Tage</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="31"/>
        <location filename="../ui/settings_pages/maintenance.py" line="53"/>
        <location filename="../ui/settings_pages/maintenance.py" line="181"/>
        <source>never</source>
        <translation>nie</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="199"/>
        <source>No working copies on disk.</source>
        <translation>Keine Arbeitskopien auf der Festplatte.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="203"/>
        <source>%d working copy/copies using %s</source>
        <translation>%d Arbeitskopie(n), die %s belegen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="219"/>
        <location filename="../ui/settings_pages/maintenance.py" line="224"/>
        <location filename="../ui/settings_pages/maintenance.py" line="249"/>
        <source>Working copies</source>
        <translation>Arbeitskopien</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="220"/>
        <source>There are no working copies to delete.</source>
        <translation>Es gibt keine Arbeitskopien zum Löschen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="250"/>
        <source>Deleted %d file(s), freeing %s.</source>
        <translation>%d Datei(en) gelöscht, %s freigegeben.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="142"/>
        <source>Working copy folder</source>
        <translation>Ordner für Arbeitskopien</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="148"/>
        <source>Leave blank to use the system temporary folder, shown above as the placeholder. A working copy is roughly the size of the recording it was made from, so somewhere with room for several of them is worth choosing - on Windows the system folder is on the system drive, which is usually the smallest. If the folder set here goes missing or cannot be written to, the system folder is used instead.</source>
        <translation>Leer lassen, um den temporären Systemordner zu verwenden, der oben als Platzhalter angezeigt wird. Eine Arbeitskopie ist etwa so groß wie die Aufnahme, aus der sie entstanden ist; es lohnt sich also, einen Ort mit Platz für mehrere davon zu wählen – unter Windows liegt der Systemordner auf dem Systemlaufwerk, das meist das kleinste ist. Fehlt der hier eingestellte Ordner oder kann nicht in ihn geschrieben werden, wird stattdessen der Systemordner verwendet.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="170"/>
        <source>Repairing a recording with Quick Stream Fix writes a working copy to the folder above, and the editor cuts that copy. They are kept so you can come back to a recording later, and deleted once they reach the age below.</source>
        <translation>Beim Reparieren einer Aufnahme mit der Schnellen Stream-Reparatur wird eine Arbeitskopie im obigen Ordner angelegt, die der Editor dann schneidet. Sie bleiben erhalten, damit Sie später an einer Aufnahme weiterarbeiten können, und werden gelöscht, sobald sie das unten angegebene Alter erreichen.</translation>
    </message>
</context>
<context>
    <name>MultiOpenDialog</name>
    <message>
        <location filename="../ui/multi_open_dialog.py" line="32"/>
        <source>Open Multiple Files</source>
        <translation>Mehrere Dateien öffnen</translation>
    </message>
    <message>
        <location filename="../ui/multi_open_dialog.py" line="45"/>
        <source>Add these files to the Joiner list?  Each is added as a whole file, in the order below - drag to reorder.</source>
        <translation>Diese Dateien zur Joiner-Liste hinzufügen?  Jede wird als ganze Datei in der unten stehenden Reihenfolge hinzugefügt - zum Umsortieren ziehen.</translation>
    </message>
    <message>
        <location filename="../ui/multi_open_dialog.py" line="52"/>
        <source>From %s</source>
        <translation>Aus %s</translation>
    </message>
    <message>
        <location filename="../ui/multi_open_dialog.py" line="73"/>
        <source>Sort List</source>
        <translation>Liste sortieren</translation>
    </message>
    <message>
        <location filename="../ui/multi_open_dialog.py" line="74"/>
        <source>Sort the files by name.</source>
        <translation>Dateien nach Namen sortieren.</translation>
    </message>
    <message>
        <location filename="../ui/multi_open_dialog.py" line="81"/>
        <source>Add To Joiner List</source>
        <translation>Zur Joiner-Liste hinzufügen</translation>
    </message>
</context>
<context>
    <name>PathRow</name>
    <message>
        <location filename="../ui/settings_widgets.py" line="72"/>
        <source>Remember last used folder</source>
        <translation>Zuletzt verwendeten Ordner merken</translation>
    </message>
    <message>
        <location filename="../ui/settings_widgets.py" line="73"/>
        <source>Always use this folder</source>
        <translation>Immer diesen Ordner verwenden</translation>
    </message>
    <message>
        <location filename="../ui/settings_widgets.py" line="80"/>
        <source>(no folder set)</source>
        <translation>(kein Ordner festgelegt)</translation>
    </message>
    <message>
        <location filename="../ui/settings_widgets.py" line="83"/>
        <source>Browse…</source>
        <translation>Durchsuchen…</translation>
    </message>
    <message>
        <location filename="../ui/settings_widgets.py" line="100"/>
        <source>Choose folder</source>
        <translation>Ordner auswählen</translation>
    </message>
</context>
<context>
    <name>PlainFolderRow</name>
    <message>
        <location filename="../ui/settings_widgets.py" line="132"/>
        <source>Browse…</source>
        <translation>Durchsuchen…</translation>
    </message>
    <message>
        <location filename="../ui/settings_widgets.py" line="142"/>
        <source>Choose folder</source>
        <translation>Ordner auswählen</translation>
    </message>
</context>
<context>
    <name>ProfileEditDialog</name>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="331"/>
        <location filename="../ui/profile_manager_dialog.py" line="716"/>
        <location filename="../ui/profile_manager_dialog.py" line="731"/>
        <source>Output Profile</source>
        <translation>Ausgabeprofil</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="347"/>
        <source>Profile name:</source>
        <translation>Profilname:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="349"/>
        <source>Container:</source>
        <translation>Container:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="352"/>
        <source>Video:</source>
        <translation>Video:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="373"/>
        <source>How far apart keyframes are placed - VideoReDo called this Max GOP length. Wider spacing makes a smaller file at the same quality; closer spacing makes seeking finer and re-cutting the result quicker. Automatic uses 5 seconds for HEVC and 1 second when cropping.</source>
        <translation>Der Abstand, in dem Keyframes gesetzt werden – in VideoReDo hieß das „Max GOP length“. Ein größerer Abstand ergibt bei gleicher Qualität eine kleinere Datei, ein kleinerer Abstand macht das Suchen feiner und das erneute Schneiden schneller. Automatisch verwendet 5 Sekunden für HEVC und 1 Sekunde beim Zuschneiden.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="380"/>
        <source>Audio:</source>
        <translation>Audio:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="384"/>
        <source>AAC bitrate:</source>
        <translation>AAC-Bitrate:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="364"/>
        <location filename="../ui/profile_manager_dialog.py" line="369"/>
        <location filename="../ui/profile_manager_dialog.py" line="385"/>
        <source>Automatic</source>
        <translation>Automatisch</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="359"/>
        <source>Encoder speed:</source>
        <translation>Encoder-Geschwindigkeit:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="362"/>
        <source>Quality (CRF):</source>
        <translation>Qualität (CRF):</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="367"/>
        <source>Keyframes every:</source>
        <translation>Keyframes alle:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="370"/>
        <source> seconds</source>
        <translation> Sekunden</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="387"/>
        <source>%d kbps</source>
        <translation>%d kbit/s</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="390"/>
        <source>The bitrate used whenever the audio is encoded to AAC - either because Audio is set to AAC, or because surround is being downmixed.&lt;br&gt;&lt;br&gt;Automatic lets ffmpeg choose, which works out at around 128 kbps. That is thin for a surround track downmixed from a Blu-ray; 256 kbps or more suits those better.</source>
        <translation>Die Bitrate, die immer dann verwendet wird, wenn der Ton nach AAC kodiert wird – entweder weil Audio auf AAC steht oder weil Surround heruntergemischt wird.&lt;br&gt;&lt;br&gt;Bei „Automatisch“ wählt ffmpeg selbst, was etwa 128 kbps ergibt. Für eine von einer Blu-ray heruntergemischte Surround-Spur ist das dünn; 256 kbps oder mehr passen dort besser.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="397"/>
        <source>Surround audio:</source>
        <translation>Surround-Ton:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="398"/>
        <source>Keep as it is</source>
        <translation>Unverändert lassen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="411"/>
        <source>Loudness:</source>
        <translation>Lautheit:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="412"/>
        <source>Leave alone</source>
        <translation>Unverändert lassen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="413"/>
        <source>Normalise (EBU R128)</source>
        <translation>Normalisieren (EBU R128)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="414"/>
        <source>Compress dynamic range</source>
        <translation>Dynamikumfang komprimieren</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="415"/>
        <source>Change level</source>
        <translation>Pegel ändern</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="418"/>
        <source>&lt;b&gt;Normalise&lt;/b&gt; brings the whole programme to a set loudness, the way broadcasters do. -23 LUFS is the broadcast standard; -16 suits headphones and quiet rooms.&lt;br&gt;&lt;br&gt;&lt;b&gt;Compress dynamic range&lt;/b&gt; lifts quiet dialogue without the loud moments becoming painful - useful for drama mixed very quietly.&lt;br&gt;&lt;br&gt;&lt;b&gt;Change level&lt;/b&gt; applies a plain gain, up or down.&lt;br&gt;&lt;br&gt;Any of these re-encodes the audio; leaving it alone keeps the lossless copy.</source>
        <translation>&lt;b&gt;Normalisieren&lt;/b&gt; bringt die gesamte Sendung auf eine festgelegte Lautheit, so wie es Sender tun. -23 LUFS ist der Rundfunkstandard; -16 passt besser für Kopfhörer und ruhige Räume.&lt;br&gt;&lt;br&gt;&lt;b&gt;Dynamikumfang komprimieren&lt;/b&gt; hebt leise Dialoge an, ohne dass die lauten Stellen unangenehm werden – nützlich bei sehr leise abgemischten Serien.&lt;br&gt;&lt;br&gt;&lt;b&gt;Pegel ändern&lt;/b&gt; wendet eine einfache Verstärkung nach oben oder unten an.&lt;br&gt;&lt;br&gt;Alle drei kodieren den Ton neu; „Unverändert lassen“ behält die verlustfreie Kopie.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="430"/>
        <source>Target:</source>
        <translation>Zielwert:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="439"/>
        <source>Audio delay:</source>
        <translation>Ton-Verzögerung:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="442"/>
        <source> ms</source>
        <translation> ms</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="445"/>
        <source>Shifts the sound relative to the picture, for a recording that arrived out of sync.&lt;br&gt;&lt;br&gt;Use a positive value when the sound is early, negative when it lags. The audio is still copied losslessly - only its timing changes.</source>
        <translation>Verschiebt den Ton gegenüber dem Bild – für eine Aufnahme, die nicht synchron ankam.&lt;br&gt;&lt;br&gt;Ein positiver Wert, wenn der Ton zu früh kommt, ein negativer, wenn er nachhinkt. Der Ton wird weiterhin verlustfrei kopiert; nur seine zeitliche Lage ändert sich.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="451"/>
        <source>Display aspect:</source>
        <translation>Anzeigeseitenverhältnis:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="454"/>
        <source>Cropping:</source>
        <translation>Zuschneiden:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="463"/>
        <source>Crop pixels:</source>
        <translation>Zuschneide-Pixel:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="497"/>
        <source>Preview…</source>
        <translation>Vorschau…</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="504"/>
        <source>Default directory:</source>
        <translation>Standardverzeichnis:</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="510"/>
        <source>(use the export folder)</source>
        <translation>(Exportordner verwenden)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="512"/>
        <source>Choose…</source>
        <translation>Auswählen…</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="514"/>
        <source>Clear</source>
        <translation>Leeren</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="521"/>
        <source>Display aspect is applied losslessly on export: 4:3 or 16:9 is stamped into the video&apos;s aspect signalling without re-encoding, so a wrongly-flagged recording plays at the right shape.  &apos;Source&apos; leaves it untouched.

Cropping removes black bars, but unlike everything else it re-encodes the video (slower, not lossless).  &apos;Auto-detect&apos; finds the bars per file; &apos;Fixed pixels&apos; uses the amounts above.

Encoder speed and Quality apply only when the video is re-encoded (HEVC, or cropping).  Slower presets give better quality for the same size, at the cost of time.  A lower CRF means better quality and a bigger file; &apos;Automatic&apos; picks a sensible value for the codec, which is what Snipwright has always used.</source>
        <translation>Das Anzeige-Seitenverhältnis wird beim Export verlustfrei angewendet: 4:3 oder 16:9 wird ohne Neukodierung in die Seitenverhältnis-Signalisierung des Videos geschrieben, sodass eine falsch gekennzeichnete Aufnahme in der richtigen Form wiedergegeben wird.  &apos;Quelle&apos; lässt es unverändert.

Das Zuschneiden entfernt schwarze Balken, kodiert das Video aber - anders als alles andere - neu (langsamer, nicht verlustfrei).  &apos;Automatisch erkennen&apos; findet die Balken pro Datei; &apos;Feste Pixel&apos; verwendet die Werte oben.

Encoder-Geschwindigkeit und Qualität gelten nur, wenn das Video neu kodiert wird (HEVC oder Zuschneiden).  Langsamere Voreinstellungen liefern bei gleicher Größe eine bessere Qualität, kosten aber Zeit.  Ein niedrigerer CRF bedeutet bessere Qualität und eine größere Datei; &apos;Automatisch&apos; wählt einen sinnvollen Wert für den Codec - genau das, was Snipwright bisher immer verwendet hat.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="633"/>
        <source> LUFS</source>
        <translation> LUFS</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="640"/>
        <source> dB</source>
        <translation> dB</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="722"/>
        <source>A CRF below 18 gives very large files for little visible gain.</source>
        <translation>Ein CRF unter 18 erzeugt sehr große Dateien bei kaum sichtbarem Gewinn.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="727"/>
        <source>A CRF above 30 is likely to show visible compression artefacts.</source>
        <translation>Ein CRF über 30 führt wahrscheinlich zu sichtbaren Kompressionsartefakten.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="732"/>
        <source>%s

Use it anyway?</source>
        <translation>%s

Trotzdem verwenden?</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="593"/>
        <source>Set cropping to Auto-detect or Fixed to preview.</source>
        <translation>Stellen Sie das Zuschneiden auf Automatisch erkennen oder Fest ein, um eine Vorschau anzuzeigen.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="399"/>
        <source>Downmix to stereo</source>
        <translation>Downmix auf Stereo</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="403"/>
        <source>A 5.1 broadcast mix played through two speakers often has very quiet dialogue, because the centre channel carrying it isn&apos;t there. Downmixing to stereo puts the dialogue back into both speakers.&lt;br&gt;&lt;br&gt;Only tracks with more than two channels are affected, and those are re-encoded; everything else is copied untouched.</source>
        <translation>Eine 5.1-Sendemischung über zwei Lautsprecher hat oft sehr leise Dialoge, weil der Center-Kanal fehlt, der sie trägt. Ein Downmix auf Stereo legt die Dialoge wieder auf beide Lautsprecher.&lt;br&gt;&lt;br&gt;Betroffen sind nur Spuren mit mehr als zwei Kanälen; diese werden neu kodiert, alles andere wird unverändert kopiert.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="598"/>
        <source>Open a recording first to preview the crop.</source>
        <translation>Öffnen Sie zuerst eine Aufnahme, um die Vorschau des Zuschneidens anzuzeigen.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="708"/>
        <source>Choose default output folder</source>
        <translation>Standard-Ausgabeordner wählen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="716"/>
        <source>Please give the profile a name.</source>
        <translation>Bitte geben Sie dem Profil einen Namen.</translation>
    </message>
</context>
<context>
    <name>ProfileEditor</name>
    <message>
        <location filename="../addons/output_profiles.py" line="23"/>
        <location filename="../addons/output_profiles.py" line="182"/>
        <location filename="../addons/output_profiles.py" line="335"/>
        <location filename="../ui/profile_manager_dialog.py" line="61"/>
        <source>Match Source</source>
        <translation>Wie Quelle</translation>
    </message>
    <message>
        <location filename="../addons/output_profiles.py" line="24"/>
        <location filename="../addons/output_profiles.py" line="337"/>
        <location filename="../ui/profile_manager_dialog.py" line="62"/>
        <source>Matroska MKV</source>
        <translation>Matroska MKV</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="66"/>
        <source>Copy (lossless)</source>
        <translation>Kopieren (verlustfrei)</translation>
    </message>
    <message>
        <location filename="../addons/output_profiles.py" line="181"/>
        <location filename="../ui/profile_manager_dialog.py" line="67"/>
        <source>HEVC (re-encode)</source>
        <translation>HEVC (neu kodieren)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="70"/>
        <source>Smart copy (lossless)</source>
        <translation>Smart-Copy (verlustfrei)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="71"/>
        <source>Re-encode to AAC</source>
        <translation>In AAC neu kodieren</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="75"/>
        <source>Source</source>
        <translation>Quelle</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="82"/>
        <source>Slower (best quality)</source>
        <translation>Langsamer (beste Qualität)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="83"/>
        <source>Slow</source>
        <translation>Langsam</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="84"/>
        <source>Default</source>
        <translation>Standard</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="85"/>
        <source>Fast</source>
        <translation>Schnell</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="86"/>
        <source>Fastest (lowest quality)</source>
        <translation>Am schnellsten (geringste Qualität)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="90"/>
        <source>None (lossless)</source>
        <translation>Keines (verlustfrei)</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="91"/>
        <source>Auto-detect bars</source>
        <translation>Balken automatisch erkennen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="92"/>
        <source>Fixed pixels</source>
        <translation>Feste Pixel</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="169"/>
        <location filename="../ui/profile_manager_dialog.py" line="477"/>
        <source>Top</source>
        <translation>Oben</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="170"/>
        <location filename="../ui/profile_manager_dialog.py" line="478"/>
        <source>Bottom</source>
        <translation>Unten</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="171"/>
        <location filename="../ui/profile_manager_dialog.py" line="479"/>
        <source>Left</source>
        <translation>Links</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="172"/>
        <location filename="../ui/profile_manager_dialog.py" line="480"/>
        <source>Right</source>
        <translation>Rechts</translation>
    </message>
    <message>
        <location filename="../addons/output_profiles.py" line="190"/>
        <source>Smart</source>
        <translation>Intelligent</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="72"/>
        <source>No audio (silent)</source>
        <translation>Kein Ton (stumm)</translation>
    </message>
</context>
<context>
    <name>ProfileManagerDialog</name>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="775"/>
        <source>Manage Output Profiles</source>
        <translation>Ausgabeprofile verwalten</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="787"/>
        <source>On</source>
        <translation>Ein</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="787"/>
        <source>Fav</source>
        <translation>Fav</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="787"/>
        <source>Profile</source>
        <translation>Profil</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="788"/>
        <source>Codec</source>
        <translation>Codec</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="788"/>
        <source>Container</source>
        <translation>Container</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="788"/>
        <source>Output Mode</source>
        <translation>Ausgabemodus</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="806"/>
        <source>Add…</source>
        <translation>Hinzufügen…</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="807"/>
        <source>Edit…</source>
        <translation>Bearbeiten…</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="808"/>
        <source>Duplicate</source>
        <translation>Duplizieren</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="809"/>
        <source>Delete</source>
        <translation>Löschen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="810"/>
        <source>Move Up</source>
        <translation>Nach oben</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="811"/>
        <source>Move Down</source>
        <translation>Nach unten</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="897"/>
        <location filename="../ui/profile_manager_dialog.py" line="935"/>
        <source>Built-in profile</source>
        <translation>Integriertes Profil</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="899"/>
        <source>“%s” is a built-in profile and can&apos;t be edited here.  Use Duplicate to make your own editable copy.</source>
        <translation>„%s“ ist ein integriertes Profil und kann hier nicht bearbeitet werden.  Verwenden Sie „Duplizieren“, um eine eigene bearbeitbare Kopie zu erstellen.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="936"/>
        <source>“%s” is a built-in profile and can&apos;t be deleted.</source>
        <translation>„%s“ ist ein integriertes Profil und kann nicht gelöscht werden.</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="941"/>
        <source>Delete Profile</source>
        <translation>Profil löschen</translation>
    </message>
    <message>
        <location filename="../ui/profile_manager_dialog.py" line="942"/>
        <source>Delete the profile “%s”?</source>
        <translation>Das Profil „%s“ löschen?</translation>
    </message>
</context>
<context>
    <name>ProgramInfo</name>
    <message>
        <location filename="../utils/program_info.py" line="23"/>
        <source>N/A</source>
        <translation>k. A.</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="126"/>
        <source>Unknown</source>
        <translation>Unbekannt</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="129"/>
        <location filename="../utils/program_info.py" line="394"/>
        <source>Progressive</source>
        <translation>Progressiv</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="131"/>
        <source>Interlaced (top field first)</source>
        <translation>Zeilensprung (oberes Halbbild zuerst)</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="134"/>
        <source>Interlaced (bottom field first)</source>
        <translation>Zeilensprung (unteres Halbbild zuerst)</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="136"/>
        <source>Interlaced</source>
        <translation>Zeilensprung</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="331"/>
        <source>File</source>
        <translation>Datei</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="332"/>
        <source>Name</source>
        <translation>Name</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="333"/>
        <source>Size</source>
        <translation>Größe</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="334"/>
        <source>Duration</source>
        <translation>Dauer</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="335"/>
        <source>Mux type</source>
        <translation>Mux-Typ</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="350"/>
        <source>Constant</source>
        <translation>Konstant</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="384"/>
        <source>Video</source>
        <translation>Video</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="385"/>
        <source>Encoding</source>
        <translation>Kodierung</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="386"/>
        <source>Stream ID</source>
        <translation>Stream-ID</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="387"/>
        <source>Frame rate</source>
        <translation>Bildrate</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="388"/>
        <source>Frame rate flag</source>
        <translation>Bildraten-Flag</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="389"/>
        <source>Encoding size</source>
        <translation>Kodierungsgröße</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="390"/>
        <source>Aspect ratio</source>
        <translation>Seitenverhältnis</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="391"/>
        <source>Header bit rate</source>
        <translation>Header-Bitrate</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="392"/>
        <source>VBV buffer</source>
        <translation>VBV-Puffer</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="393"/>
        <source>Profile</source>
        <translation>Profil</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="395"/>
        <source>Chroma</source>
        <translation>Chroma</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="396"/>
        <source>Entropy mode</source>
        <translation>Entropiemodus</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="397"/>
        <location filename="../utils/program_info.py" line="471"/>
        <source>Bit rate</source>
        <translation>Bitrate</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="462"/>
        <location filename="../utils/program_info.py" line="533"/>
        <source>Audio Stream: %d%s</source>
        <translation>Audiospur: %d%s</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="463"/>
        <location filename="../utils/program_info.py" line="530"/>
        <source> (Primary)</source>
        <translation> (primär)</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="465"/>
        <source>Codec</source>
        <translation>Codec</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="466"/>
        <source>Format</source>
        <translation>Format</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="467"/>
        <source>Channels</source>
        <translation>Kanäle</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="468"/>
        <location filename="../utils/program_info.py" line="491"/>
        <source>Language</source>
        <translation>Sprache</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="469"/>
        <location filename="../utils/program_info.py" line="492"/>
        <source>PID</source>
        <translation>PID</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="470"/>
        <source>PES Stream Id</source>
        <translation>PES-Stream-ID</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="472"/>
        <source>Sampling rate</source>
        <translation>Abtastrate</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="473"/>
        <source>Sample size</source>
        <translation>Abtastgröße</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="254"/>
        <source>DVB subtitles</source>
        <translation>DVB-Untertitel</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="255"/>
        <source>DVB teletext</source>
        <translation>DVB-Videotext</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="256"/>
        <source>PGS (Blu-ray)</source>
        <translation>PGS (Blu-ray)</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="257"/>
        <source>DVD subtitles</source>
        <translation>DVD-Untertitel</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="258"/>
        <source>SubRip text</source>
        <translation>SubRip-Text</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="259"/>
        <source>ASS text</source>
        <translation>ASS-Text</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="260"/>
        <source>MP4 text</source>
        <translation>MP4-Text</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="488"/>
        <location filename="../utils/program_info.py" line="538"/>
        <source>Subtitle Stream: %d</source>
        <translation>Untertitelspur: %d</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="490"/>
        <source>Type</source>
        <translation>Typ</translation>
    </message>
    <message>
        <location filename="../utils/program_info.py" line="493"/>
        <source>Page</source>
        <translation>Seite</translation>
    </message>
</context>
<context>
    <name>ProgramInfoDialog</name>
    <message>
        <location filename="../ui/program_info_dialog.py" line="35"/>
        <source>Programme Information</source>
        <translation>Programminformationen</translation>
    </message>
    <message>
        <location filename="../ui/program_info_dialog.py" line="121"/>
        <source>Copy to clipboard</source>
        <translation>In die Zwischenablage kopieren</translation>
    </message>
    <message>
        <location filename="../ui/program_info_dialog.py" line="127"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
</context>
<context>
    <name>Renamer</name>
    <message>
        <location filename="../ui/renamer_dialog.py" line="95"/>
        <source>Show (Year) / Season 02 / Episode</source>
        <translation>Serie (Jahr) / Staffel 02 / Episode</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="96"/>
        <source>Show (Year) / Season 2 / Episode</source>
        <translation>Serie (Jahr) / Staffel 2 / Episode</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="97"/>
        <source>Flat - no folders</source>
        <translation>Flach - keine Ordner</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="71"/>
        <source>Film (Year) in its own folder</source>
        <translation>Film (Jahr) in eigenem Ordner</translation>
    </message>
    <message>
        <location filename="../ui/film_renamer_dialog.py" line="72"/>
        <source>Flat - Film (Year)</source>
        <translation>Flach - Film (Jahr)</translation>
    </message>
</context>
<context>
    <name>RenamerDialog</name>
    <message>
        <location filename="../ui/renamer_dialog.py" line="311"/>
        <location filename="../ui/renamer_dialog.py" line="728"/>
        <location filename="../ui/renamer_dialog.py" line="814"/>
        <location filename="../ui/renamer_dialog.py" line="872"/>
        <location filename="../ui/renamer_dialog.py" line="969"/>
        <location filename="../ui/renamer_dialog.py" line="1083"/>
        <location filename="../ui/renamer_dialog.py" line="1109"/>
        <location filename="../ui/renamer_dialog.py" line="1214"/>
        <location filename="../ui/renamer_dialog.py" line="1252"/>
        <location filename="../ui/renamer_dialog.py" line="1261"/>
        <location filename="../ui/renamer_dialog.py" line="1281"/>
        <location filename="../ui/renamer_dialog.py" line="1297"/>
        <location filename="../ui/renamer_dialog.py" line="1304"/>
        <location filename="../ui/renamer_dialog.py" line="1397"/>
        <location filename="../ui/renamer_dialog.py" line="1419"/>
        <location filename="../ui/renamer_dialog.py" line="1424"/>
        <source>TV Renamer</source>
        <translation>TV-Umbenerner</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="318"/>
        <source>Source</source>
        <translation>Quelle</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="320"/>
        <source>Choose Folder…</source>
        <translation>Ordner auswählen…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="322"/>
        <source>Add Files…</source>
        <translation>Dateien hinzufügen…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="324"/>
        <source>Refresh</source>
        <translation>Aktualisieren</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="325"/>
        <source>Re-scan the current folder for new files</source>
        <translation>Aktuellen Ordner erneut nach neuen Dateien durchsuchen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="328"/>
        <location filename="../ui/renamer_dialog.py" line="778"/>
        <source>No files chosen.</source>
        <translation>Keine Dateien ausgewählt.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="329"/>
        <source>Load last folder on open</source>
        <translation>Beim Öffnen den letzten Ordner laden</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="331"/>
        <source>When ticked, the renamer opens straight into the folder you used last.</source>
        <translation>Wenn aktiviert, öffnet sich der Umbenenner direkt in dem Ordner, den Sie zuletzt verwendet haben.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="347"/>
        <source>Series (used when auto-match is off)</source>
        <translation>Serie (wird verwendet, wenn automatische Zuordnung aus ist)</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="350"/>
        <source>Series name to search for</source>
        <translation>Name der Serie, nach der gesucht werden soll</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="352"/>
        <source>Search TMDB</source>
        <translation>TMDB durchsuchen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="368"/>
        <source>Preset:</source>
        <translation>Voreinstellung:</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="372"/>
        <source>Save…</source>
        <translation>Speichern…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="374"/>
        <source>Save the current pattern as a named preset</source>
        <translation>Das aktuelle Muster als benannte Voreinstellung speichern</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="378"/>
        <source>Delete</source>
        <translation>Löschen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="379"/>
        <source>Delete the selected saved preset</source>
        <translation>Die ausgewählte gespeicherte Voreinstellung löschen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="386"/>
        <source>Pattern:</source>
        <translation>Muster:</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="393"/>
        <source>Codes…</source>
        <translation>Codes…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="395"/>
        <source>Pattern codes</source>
        <translation>Muster-Codes</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="398"/>
        <source>Match TV Shows</source>
        <translation>Serien zuordnen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="417"/>
        <source>Destination:</source>
        <translation>Zielort:</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="421"/>
        <source>Choose…</source>
        <translation>Auswählen…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="423"/>
        <source>Clear</source>
        <translation>Leeren</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="438"/>
        <source>Overwrite files that already exist at the destination</source>
        <translation>Dateien überschreiben, die am Zielort bereits existieren</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="443"/>
        <source>Auto-match every show in one pass  (double-click a row to change its show)</source>
        <translation>Alle Serien in einem Durchgang automatisch zuordnen (Doppelklick auf eine Zeile, um deren Serie zu ändern)</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="455"/>
        <source>Current name</source>
        <translation>Aktueller Name</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="455"/>
        <source>New name</source>
        <translation>Neuer Name</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="455"/>
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="470"/>
        <source>Process Ticked</source>
        <translation>Ausgewählte verarbeiten</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="473"/>
        <source>Clear Completed</source>
        <translation>Abgeschlossene leeren</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="476"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="585"/>
        <source>Custom…</source>
        <translation>Benutzerdefiniert…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="607"/>
        <location filename="../ui/renamer_dialog.py" line="611"/>
        <source>Save preset</source>
        <translation>Voreinstellung speichern</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="607"/>
        <source>There&apos;s no pattern to save.</source>
        <translation>Es gibt kein Muster zum Speichern.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="611"/>
        <source>Name for this preset:</source>
        <translation>Name für dieses Preset:</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="641"/>
        <source>Delete preset</source>
        <translation>Voreinstellung löschen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="671"/>
        <source>e.g.   %s</source>
        <translation>z. B.   %s</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="693"/>
        <source>Choose destination library folder</source>
        <translation>Zielordner für die Mediathek auswählen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="729"/>
        <source>No TMDB API key set. Add one in Settings (the TMDB API key field on the General page), then try again.</source>
        <translation>Kein TMDB-API-Schlüssel festgelegt. Fügen Sie einen in den Einstellungen hinzu (das Feld TMDB-API-Schlüssel auf der Registerkarte Allgemein) und versuchen Sie es erneut.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="791"/>
        <source>Choose folder</source>
        <translation>Ordner auswählen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="814"/>
        <source>No video files found in that folder.</source>
        <translation>Keine Videodateien in diesem Ordner gefunden.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="877"/>
        <source>(no matches)</source>
        <translation>(keine Treffer)</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="907"/>
        <source>Choose the right show</source>
        <translation>Wählen Sie die richtige Serie</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="913"/>
        <source>Search</source>
        <translation>Suchen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="924"/>
        <location filename="../ui/renamer_dialog.py" line="1034"/>
        <source>Season:</source>
        <translation>Staffel:</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="930"/>
        <source>Episode(s):</source>
        <translation>Episode(n):</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="934"/>
        <source>e.g. 11  or  11-12</source>
        <translation>z. B. 11  oder  11-12</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="939"/>
        <source>Set the season and episode here if they aren&apos;t in the file name.</source>
        <translation>Legen Sie Staffel und Episode hier fest, falls sie nicht im Dateinamen enthalten sind.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="945"/>
        <source>Use This Show</source>
        <translation>Diese Serie verwenden</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="947"/>
        <location filename="../ui/renamer_dialog.py" line="1050"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="976"/>
        <source>%s (%s)</source>
        <translation>%s (%s)</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1022"/>
        <source>Pick episode</source>
        <translation>Episode auswählen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1029"/>
        <source>Change show…</source>
        <translation>Serie ändern…</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1043"/>
        <source>Pick the episode (Ctrl-click for a two-parter).</source>
        <translation>Wählen Sie die Episode aus (Strg-Klick für einen Zweiteiler).</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1048"/>
        <source>Select episode</source>
        <translation>Episode auswählen</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1120"/>
        <source>Specials</source>
        <translation>Specials</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1121"/>
        <source>Season %d</source>
        <translation>Staffel %d</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1241"/>
        <source>Done</source>
        <translation>Fertig</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1245"/>
        <source>not matched yet</source>
        <translation>noch nicht zugeordnet</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1247"/>
        <source>Rename Not Required</source>
        <translation>Umbenennung nicht erforderlich</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1248"/>
        <source>Ready</source>
        <translation>Bereit</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1252"/>
        <source>Choose some files first.</source>
        <translation>Wählen Sie zuerst einige Dateien aus.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1261"/>
        <source>Everything in the list is done already.</source>
        <translation>Alles in der Liste ist bereits erledigt.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1282"/>
        <source>Search for and choose a series first, or tick &apos;Auto-match every show in one pass&apos;.</source>
        <translation>Suchen und wählen Sie zuerst eine Serie aus oder aktivieren Sie „Alle Serien in einem Durchgang automatisch zuordnen“.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1397"/>
        <source>Nothing is ticked to rename.</source>
        <translation>Es wurde nichts zum Umbenennen ausgewählt.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="642"/>
        <source>Delete the preset &apos;%s&apos;?</source>
        <translation>Die Voreinstellung „%s“ löschen?</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="773"/>
        <source>%d file(s) loaded.</source>
        <translation>%d Datei(en) geladen.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1369"/>
        <source>%(ready)d ready · %(done)d done · %(total)d total   —   double-click a row to change its show.</source>
        <translation>%(ready)d bereit · %(done)d erledigt · %(total)d gesamt   —   Doppelklicken Sie auf eine Zeile, um ihre Sendung zu ändern.</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1425"/>
        <source>Renamed %d file(s).%s%s</source>
        <translation>%d Datei(en) umbenannt.%s%s</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1428"/>
        <source>
Skipped %d (target already exists).</source>
        <translation>
%d übersprungen (Ziel existiert bereits).</translation>
    </message>
    <message>
        <location filename="../ui/renamer_dialog.py" line="1430"/>
        <source>
Failed %d.</source>
        <translation>
%d fehlgeschlagen.</translation>
    </message>
</context>
<context>
    <name>SaveVideoDialog</name>
    <message>
        <location filename="../ui/save_video_dialog.py" line="41"/>
        <location filename="../ui/save_video_dialog.py" line="233"/>
        <location filename="../ui/save_video_dialog.py" line="435"/>
        <location filename="../ui/save_video_dialog.py" line="438"/>
        <location filename="../ui/save_video_dialog.py" line="448"/>
        <source>Save Video</source>
        <translation>Video speichern</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="76"/>
        <source>Output File</source>
        <translation>Ausgabedatei</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="84"/>
        <source>Folders</source>
        <translation>Ordner</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="86"/>
        <source>Send this export to one of your favourite folders.&lt;br&gt;Set them up under Settings → Files &amp; folders.</source>
        <translation>Speichert diesen Export in einem Ihrer Favoriten-Ordner.&lt;br&gt;Einrichten unter Einstellungen → Dateien &amp; Ordner.</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="94"/>
        <source>Select File</source>
        <translation>Datei auswählen</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="100"/>
        <location filename="../ui/save_video_dialog.py" line="118"/>
        <source>Profile</source>
        <translation>Profil</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="105"/>
        <source>Profile Options…</source>
        <translation>Profiloptionen…</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="107"/>
        <source>Tweak the selected profile for this export only - the change isn&apos;t saved, so built-in profiles revert next time.  Manage and save profiles permanently from Tools → Manage Profiles.</source>
        <translation>Das gewählte Profil nur für diesen Export anpassen - die Änderung wird nicht gespeichert, integrierte Profile setzen sich beim nächsten Mal zurück.  Profile dauerhaft verwalten und speichern unter Werkzeuge → Profile verwalten.</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="118"/>
        <source>Codec</source>
        <translation>Codec</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="118"/>
        <source>Container</source>
        <translation>Container</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="118"/>
        <source>Output Mode</source>
        <translation>Ausgabemodus</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="134"/>
        <source>Favourites Only</source>
        <translation>Nur Favoriten</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="233"/>
        <location filename="../ui/save_video_dialog.py" line="435"/>
        <source>Please choose a profile.</source>
        <translation>Bitte wählen Sie ein Profil.</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="376"/>
        <source>No favourite folders set</source>
        <translation>Keine Favoriten-Ordner festgelegt</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="389"/>
        <source>%s (not available)</source>
        <translation>%s (nicht verfügbar)</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="420"/>
        <source>Save Video As</source>
        <translation>Video speichern unter</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="438"/>
        <source>Please choose an output file.</source>
        <translation>Bitte wählen Sie eine Ausgabedatei.</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="205"/>
        <location filename="../ui/save_video_dialog.py" line="247"/>
        <source>%s  —  edited for this export</source>
        <translation>%s  —  für diesen Export bearbeitet</translation>
    </message>
    <message>
        <location filename="../ui/save_video_dialog.py" line="449"/>
        <source>%s already exists.

Overwrite it?</source>
        <translation>%s existiert bereits.

Überschreiben?</translation>
    </message>
</context>
<context>
    <name>SceneList</name>
    <message>
        <location filename="../ui/scene_list.py" line="37"/>
        <location filename="../ui/scene_list.py" line="125"/>
        <source>Scene Start</source>
        <translation>Szenenanfang</translation>
    </message>
    <message>
        <location filename="../ui/scene_list.py" line="38"/>
        <location filename="../ui/scene_list.py" line="126"/>
        <source>Scene End</source>
        <translation>Szenenende</translation>
    </message>
    <message>
        <location filename="../ui/scene_list.py" line="39"/>
        <location filename="../ui/scene_list.py" line="121"/>
        <location filename="../ui/scene_list.py" line="127"/>
        <source>Duration</source>
        <translation>Dauer</translation>
    </message>
    <message>
        <location filename="../ui/scene_list.py" line="119"/>
        <source>Cut Start</source>
        <translation>Schnitt Anfang</translation>
    </message>
    <message>
        <location filename="../ui/scene_list.py" line="120"/>
        <source>Cut End</source>
        <translation>Schnitt Ende</translation>
    </message>
</context>
<context>
    <name>Settings</name>
    <message>
        <location filename="../ui/settings_pages/files.py" line="28"/>
        <source>Files &amp; folders</source>
        <translation>Dateien &amp; Ordner</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="11"/>
        <source>None</source>
        <translation>Keine</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="12"/>
        <source>Thumbnails</source>
        <translation>Vorschaubilder</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="13"/>
        <source>Preview</source>
        <translation>Vorschau</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="14"/>
        <source>Both</source>
        <translation>Beide</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="18"/>
        <source>Cut Mode</source>
        <translation>Schnittmodus</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="19"/>
        <source>Scene Mode</source>
        <translation>Szenenmodus</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="23"/>
        <source>Follow system</source>
        <translation>Systemeinstellung folgen</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="24"/>
        <source>Light</source>
        <translation>Hell</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="25"/>
        <source>Dark</source>
        <translation>Dunkel</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/general.py" line="30"/>
        <source>General</source>
        <translation>Allgemein</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/logs.py" line="11"/>
        <source>Logging</source>
        <translation>Protokollierung</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/maintenance.py" line="15"/>
        <source>Maintenance</source>
        <translation>Wartung</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="18"/>
        <source>External tools</source>
        <translation>Externe Werkzeuge</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/ad_detection.py" line="33"/>
        <source>Advert detection</source>
        <translation>Werbeerkennung</translation>
    </message>
</context>
<context>
    <name>SettingsDialog</name>
    <message>
        <location filename="../ui/settings_dialog.py" line="47"/>
        <source>Settings</source>
        <translation>Einstellungen</translation>
    </message>
    <message>
        <location filename="../ui/settings_dialog.py" line="110"/>
        <source>Restore default settings</source>
        <translation>Standardeinstellungen wiederherstellen</translation>
    </message>
    <message>
        <location filename="../ui/settings_dialog.py" line="111"/>
        <source>This resets all settings - paths, options and keyboard shortcuts - to their defaults.

Your recordings and projects are not affected. Continue?</source>
        <translation>Dies setzt alle Einstellungen – Pfade, Optionen und Tastenkombinationen – auf ihre Standardwerte zurück.

Ihre Aufnahmen und Projekte sind davon nicht betroffen. Fortfahren?</translation>
    </message>
    <message>
        <location filename="../ui/settings_dialog.py" line="183"/>
        <source>Cache cleared</source>
        <translation>Cache geleert</translation>
    </message>
</context>
<context>
    <name>TitleEditorDialog</name>
    <message>
        <location filename="../ui/joiner_dialog.py" line="71"/>
        <source>Title Card</source>
        <translation>Titelkarte</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="78"/>
        <source>Main text</source>
        <translation>Haupttext</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="80"/>
        <source>Optional second line</source>
        <translation>Optionale zweite Zeile</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="100"/>
        <source>Clear</source>
        <translation>Leeren</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="108"/>
        <source>Fill frame (may crop edges)</source>
        <translation>Bild füllen (Ränder können beschnitten werden)</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="109"/>
        <source>Fit inside (letterbox)</source>
        <translation>Einpassen (Letterbox)</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="110"/>
        <source>Stretch (may distort)</source>
        <translation>Strecken (kann verzerren)</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="115"/>
        <source>Title:</source>
        <translation>Titel:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="116"/>
        <source>Subtitle:</source>
        <translation>Untertitel:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="117"/>
        <source>Duration:</source>
        <translation>Dauer:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="118"/>
        <source>Background colour:</source>
        <translation>Hintergrundfarbe:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="119"/>
        <source>Background image:</source>
        <translation>Hintergrundbild:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="120"/>
        <source>Image scaling:</source>
        <translation>Bildskalierung:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="121"/>
        <source>Text colour:</source>
        <translation>Textfarbe:</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="163"/>
        <source>Choose image…</source>
        <translation>Bild auswählen…</translation>
    </message>
    <message>
        <location filename="../ui/joiner_dialog.py" line="170"/>
        <source>Choose background image</source>
        <translation>Hintergrundbild auswählen</translation>
    </message>
</context>
<context>
    <name>ToolsPage</name>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="38"/>
        <source>mkvmerge (part of MKVToolNix) is used for lossless MKV exports.</source>
        <translation>mkvmerge (Teil von MKVToolNix) wird für verlustfreie MKV-Exporte verwendet.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="66"/>
        <source>ffmpeg and ffprobe do the cutting, joining and stream probing. They aren&apos;t included with Snipwright and aren&apos;t always pre-installed - if they&apos;re on your PATH they&apos;re detected automatically here, otherwise install them (or download a build) and set the paths. Point these at a specific build if you want a particular version.</source>
        <translation>ffmpeg und ffprobe übernehmen das Schneiden, Zusammenfügen und Analysieren der Streams. Sie sind nicht im Lieferumfang von Snipwright enthalten und nicht immer vorinstalliert – wenn sie sich in Ihrem PATH befinden, werden sie hier automatisch erkannt, andernfalls installieren Sie sie (oder laden Sie ein Build herunter) und legen Sie die Pfade fest. Verweisen Sie auf ein bestimmtes Build, wenn Sie eine ganz bestimmte Version wünschen.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="73"/>
        <source>TMDB API key</source>
        <translation>TMDB-API-Schlüssel</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="80"/>
        <source>v3 API key from themoviedb.org/settings/api</source>
        <translation>v3-API-Schlüssel von themoviedb.org/settings/api</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="84"/>
        <source>Used by the TV and Film renamers (Extras menu) to look up titles. A free key is available from your TMDB account.</source>
        <translation>Wird von den TV- und Film-Umbenennern (Menü Extras) verwendet, um Titel nachzuschlagen. Ein kostenloser Schlüssel ist über Ihr TMDB-Konto erhältlich.</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="31"/>
        <source>mkvmerge program:</source>
        <translation>mkvmerge-Programm:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="33"/>
        <source>(path to mkvmerge - install mkvtoolnix; auto-detected if on PATH)</source>
        <translation>(Pfad zu mkvmerge – mkvtoolnix installieren; wird im PATH automatisch erkannt)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="48"/>
        <source>ffmpeg program:</source>
        <translation>ffmpeg-Programm:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="50"/>
        <source>(path to ffmpeg - auto-detected if on PATH)</source>
        <translation>(Pfad zu ffmpeg – wird im PATH automatisch erkannt)</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="59"/>
        <source>ffprobe program:</source>
        <translation>ffprobe-Programm:</translation>
    </message>
    <message>
        <location filename="../ui/settings_pages/tools.py" line="61"/>
        <source>(path to ffprobe - auto-detected if on PATH)</source>
        <translation>(Pfad zu ffprobe – wird im PATH automatisch erkannt)</translation>
    </message>
</context>
<context>
    <name>TransportControls</name>
    <message>
        <location filename="../ui/transport_panel.py" line="669"/>
        <source>Previous frame</source>
        <translation>Vorheriges Bild</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="670"/>
        <source>Play / Pause</source>
        <translation>Wiedergabe / Pause</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="671"/>
        <source>Next frame</source>
        <translation>Nächstes Bild</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="761"/>
        <location filename="../ui/transport_panel.py" line="763"/>
        <source>Back %s</source>
        <translation>%s zurück</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="762"/>
        <location filename="../ui/transport_panel.py" line="764"/>
        <source>Forward %s</source>
        <translation>%s vorwärts</translation>
    </message>
</context>
<context>
    <name>TransportPanel</name>
    <message>
        <location filename="../ui/transport_panel.py" line="166"/>
        <source>Cursor position (double-click to type a time)</source>
        <translation>Cursorposition (Doppelklick, um eine Zeit einzugeben)</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="204"/>
        <source>In point</source>
        <translation>Anfangspunkt</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="209"/>
        <source>Out point</source>
        <translation>Endpunkt</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="255"/>
        <source>Set in point at cursor</source>
        <translation>Anfangspunkt am Cursor setzen</translation>
    </message>
    <message>
        <location filename="../ui/transport_panel.py" line="256"/>
        <source>Set out point at cursor</source>
        <translation>Endpunkt am Cursor setzen</translation>
    </message>
</context>
<context>
    <name>TrimCopyDialog</name>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="93"/>
        <source>Trim and Copy Source File</source>
        <translation>Quelldatei zuschneiden und kopieren</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="116"/>
        <location filename="../ui/trim_copy_dialog.py" line="128"/>
        <source>…</source>
        <translation>…</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="119"/>
        <source>Source File:</source>
        <translation>Quelldatei:</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="123"/>
        <source>—</source>
        <translation>—</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="124"/>
        <source>Size:</source>
        <translation>Größe:</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="131"/>
        <source>Output File:</source>
        <translation>Ausgabedatei:</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="140"/>
        <source>Output Options</source>
        <translation>Ausgabeoptionen</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="144"/>
        <source>From Beginning</source>
        <translation>Vom Anfang</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="145"/>
        <source>To End Of File</source>
        <translation>Bis zum Dateiende</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="148"/>
        <source>Start At MByte:</source>
        <translation>Beginnen bei MByte:</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="157"/>
        <source>Use Selection Markers</source>
        <translation>Auswahlmarkierungen verwenden</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="175"/>
        <source>MBytes To Output:</source>
        <translation>Auszugebende MBytes:</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="199"/>
        <source>Start Copy</source>
        <translation>Kopieren starten</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="202"/>
        <location filename="../ui/trim_copy_dialog.py" line="412"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="239"/>
        <source>Select Source File</source>
        <translation>Quelldatei auswählen</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="240"/>
        <source>All files (*)</source>
        <translation>Alle Dateien (*)</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="265"/>
        <source>Select Output File</source>
        <translation>Ausgabedatei auswählen</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="323"/>
        <location filename="../ui/trim_copy_dialog.py" line="331"/>
        <location filename="../ui/trim_copy_dialog.py" line="342"/>
        <location filename="../ui/trim_copy_dialog.py" line="351"/>
        <location filename="../ui/trim_copy_dialog.py" line="355"/>
        <location filename="../ui/trim_copy_dialog.py" line="366"/>
        <location filename="../ui/trim_copy_dialog.py" line="387"/>
        <location filename="../ui/trim_copy_dialog.py" line="419"/>
        <location filename="../ui/trim_copy_dialog.py" line="426"/>
        <source>Trim and Copy</source>
        <translation>Zuschneiden und kopieren</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="266"/>
        <source>Same as source (*%s);;All files (*)</source>
        <translation>Wie die Quelle (*%s);;Alle Dateien (*)</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="324"/>
        <source>Please choose a valid source file first.</source>
        <translation>Bitte wählen Sie zuerst eine gültige Quelldatei.</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="332"/>
        <source>Could not work out byte offsets from the selection markers for this file.</source>
        <translation>Die Byte-Offsets konnten für diese Datei nicht aus den Auswahlmarkierungen ermittelt werden.</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="343"/>
        <source>That selection produces an empty file.</source>
        <translation>Diese Auswahl ergibt eine leere Datei.</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="352"/>
        <source>Please choose an output file.</source>
        <translation>Bitte wählen Sie eine Ausgabedatei.</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="356"/>
        <source>The output file must be different from the source file.</source>
        <translation>Die Ausgabedatei muss sich von der Quelldatei unterscheiden.</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="368"/>
        <source>%s files keep their index in a header at one end of the file, and a trimmed copy leaves that index describing data that is no longer there. The result will most likely not play.

To cut this recording properly, use Save Video instead, which rebuilds the file correctly.

Continue anyway?</source>
        <translation>%s-Dateien halten ihren Index in einem Header an einem Ende der Datei. Bei einer beschnittenen Kopie beschreibt dieser Index dann Daten, die nicht mehr vorhanden sind, und das Ergebnis lässt sich höchstwahrscheinlich nicht abspielen.

Um diese Aufnahme richtig zu schneiden, verwende stattdessen „Video speichern“; dabei wird die Datei korrekt neu aufgebaut.

Trotzdem fortfahren?</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="397"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="427"/>
        <source>Copy failed:

%s</source>
        <translation>Kopieren fehlgeschlagen:

%s</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="388"/>
        <source>%s already exists.

Overwrite it?</source>
        <translation>%s existiert bereits.

Überschreiben?</translation>
    </message>
    <message>
        <location filename="../ui/trim_copy_dialog.py" line="420"/>
        <source>Copy complete.

%(path)s
%(size)s written.</source>
        <translation>Kopieren abgeschlossen.

%(path)s
%(size)s geschrieben.</translation>
    </message>
</context>
<context>
    <name>UserGuideDialog</name>
    <message>
        <location filename="../ui/help_dialog.py" line="99"/>
        <source>Snipwright User Guide</source>
        <translation>Snipwright Benutzerhandbuch</translation>
    </message>
    <message>
        <location filename="../ui/help_dialog.py" line="127"/>
        <source>User guide not found</source>
        <translation>Benutzerhandbuch nicht gefunden</translation>
    </message>
    <message>
        <location filename="../ui/help_dialog.py" line="128"/>
        <source>The guide file appears to be missing from this installation.</source>
        <translation>Die Handbuchdatei scheint in dieser Installation zu fehlen.</translation>
    </message>
    <message>
        <location filename="../ui/help_dialog.py" line="135"/>
        <source>Open in Browser</source>
        <translation>Im Browser öffnen</translation>
    </message>
    <message>
        <location filename="../ui/help_dialog.py" line="139"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
</context>
<context>
    <name>VolumeControl</name>
    <message>
        <location filename="../ui/transport_panel.py" line="514"/>
        <source>Playback audio needs Qt Multimedia (e.g. pip install PySide6-Addons).</source>
        <translation>Die Audiowiedergabe erfordert Qt Multimedia (z. B. pip install PySide6-Addons).</translation>
    </message>
</context>
<context>
    <name>WatchControlDialog</name>
    <message>
        <location filename="../watch/tray.py" line="490"/>
        <source>Snipwright Watcher</source>
        <translation>Snipwright Watcher</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="529"/>
        <source>Idle.</source>
        <translation>Bereit.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="535"/>
        <source>Scan Now</source>
        <translation>Jetzt scannen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="539"/>
        <source>Open Output Folder</source>
        <translation>Ausgabeordner öffnen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="541"/>
        <source>Launch Snipwright</source>
        <translation>Snipwright starten</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="550"/>
        <source>Recording folders to watch</source>
        <translation>Zu überwachende Aufnahmeordner</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="560"/>
        <source>Add…</source>
        <translation>Hinzufügen…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="562"/>
        <source>Remove</source>
        <translation>Entfernen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="571"/>
        <source>Scanning</source>
        <translation>Scannen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="574"/>
        <source>Scan every (minutes):</source>
        <translation>Scan-Intervall (Minuten):</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="579"/>
        <source>Wait after last change (minutes):</source>
        <translation>Warten nach letzter Änderung (Minuten):</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="583"/>
        <source>How long a recording must be untouched before it&apos;s scanned, so in-progress recordings are left alone.</source>
        <translation>Wie lange eine Aufnahme unverändert sein muss, bevor sie gescannt wird, damit laufende Aufnahmen nicht angetastet werden.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="589"/>
        <source>Keep missing recordings for (hours):</source>
        <translation>Fehlende Aufnahmen behalten für (Stunden):</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="593"/>
        <source>Don&apos;t wait</source>
        <translation>Nicht warten</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="595"/>
        <source>How long a recording that has disappeared stays on the completed list before the watcher forgets it. Recordings on a network share vanish for ordinary reasons - a reboot, maintenance, a share renamed - and forgetting them at once means every one is detected again when the share comes back. A folder that can&apos;t be read at all is always left alone, whatever this is set to. Set to 0 to forget a recording as soon as it can&apos;t be seen.</source>
        <translation>Wie lange eine verschwundene Aufnahme auf der Liste der erledigten Aufnahmen bleibt, bevor die Überwachung sie vergisst. Aufnahmen auf einer Netzwerkfreigabe verschwinden aus ganz gewöhnlichen Gründen - ein Neustart, Wartungsarbeiten, eine umbenannte Freigabe - und wenn sie sofort vergessen werden, wird jede einzelne erneut geprüft, sobald die Freigabe zurück ist. Ein Ordner, der sich überhaupt nicht lesen lässt, bleibt immer unangetastet, unabhängig von dieser Einstellung. Auf 0 setzen, um eine Aufnahme sofort zu vergessen, sobald sie nicht mehr sichtbar ist.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="608"/>
        <source>Scan immediately on launch</source>
        <translation>Direkt beim Start scannen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="610"/>
        <source>Run a scan a few seconds after starting, instead of waiting for the first interval.</source>
        <translation>Führt wenige Sekunden nach dem Start einen Scan durch, anstatt auf das erste Intervall zu warten.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="616"/>
        <source>Start the watcher automatically on login</source>
        <translation>Den Watcher automatisch bei der Anmeldung starten</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="623"/>
        <source>Start-on-login isn&apos;t available on this platform.</source>
        <translation>Automatischer Start bei der Anmeldung ist auf dieser Plattform nicht verfügbar.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="628"/>
        <source>Output</source>
        <translation>Ausgabe</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="631"/>
        <source>Output folder:</source>
        <translation>Ausgabeordner:</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="635"/>
        <source>Browse…</source>
        <translation>Durchsuchen…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="641"/>
        <source>Save a full-length project even when no commercials are found</source>
        <translation>Projekt in voller Länge speichern, selbst wenn keine Werbung gefunden wurde</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="644"/>
        <source>When Comskip finds no adverts, still write a .vprj covering the whole recording, so it reaches the Batch Manager ready to review or copy.  Turn off to skip advert-free recordings entirely.</source>
        <translation>Wenn Comskip keine Werbung findet, wird dennoch eine .vprj-Datei für die gesamte Aufnahme erstellt, sodass sie zur Überprüfung oder zum Kopieren im Batch-Manager bereitsteht. Deaktivieren, um werbefreie Aufnahmen komplett zu überspringen.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="653"/>
        <source>Logs &amp;&amp; files</source>
        <translation>Protokolle &amp;&amp; Dateien</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="656"/>
        <source>Log files to keep:</source>
        <translation>Zu behaltende Protokolldateien:</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="660"/>
        <source>How many of the watcher&apos;s own per-day log files to keep. The oldest beyond this are removed when the watcher starts. Set to 0 to keep every log. (The editor keeps its logs separately.)</source>
        <translation>Wie viele der täglichen Protokolldateien des Watchers aufbewahrt werden sollen. Die ältesten darüber hinausgehenden Dateien werden beim Start des Watchers entfernt. Auf 0 setzen, um alle Protokolle zu behalten. (Der Editor speichert seine Protokolle separat.)</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="668"/>
        <source>Open config folder</source>
        <translation>Konfigurationsordner öffnen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="670"/>
        <source>Open the folder holding the watcher&apos;s settings and lists - watch_processed.txt (the completed list, delete entries to have a recording picked up again), watch_ignore.txt, and the watcher log.</source>
        <translation>Öffnet den Ordner mit den Einstellungen und Listen des Watchers – watch_processed.txt (die Liste der fertiggestellten Dateien; Einträge löschen, um eine Aufnahme erneut zu verarbeiten), watch_ignore.txt und das Watcher-Protokoll.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="688"/>
        <source>Save</source>
        <translation>Speichern</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="691"/>
        <source>Close</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="730"/>
        <source>Comskip: %s</source>
        <translation>Comskip: %s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="731"/>
        <source>
Ini: %s</source>
        <translation>
Ini: %s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="744"/>
        <source>Resume</source>
        <translation>Fortsetzen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="744"/>
        <source>Pause</source>
        <translation>Pause</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="751"/>
        <source>Add recording folder</source>
        <translation>Aufnahmeordner hinzufügen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="765"/>
        <source>Output folder</source>
        <translation>Ausgabeordner</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="784"/>
        <source>Settings saved.</source>
        <translation>Einstellungen gespeichert.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="720"/>
        <source>Detector: Chalkline (built in - nothing to set up). Change it in the Snipwright editor → Settings → Advert detection.</source>
        <translation>Detektor: Chalkline (integriert – nichts einzurichten). Ändern lässt sich das im Snipwright-Editor → Einstellungen → Werbeerkennung.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="736"/>
        <source>⚠ Comskip isn&apos;t set. Open the Snipwright editor → Settings and set the Comskip program (and .ini), or switch to Chalkline there - it is built in and needs no setup. The watcher reads the choice from there.</source>
        <translation>⚠ Comskip ist nicht festgelegt. Öffnen Sie den Snipwright-Editor → Einstellungen und legen Sie das Comskip-Programm (und die .ini) fest, oder wechseln Sie dort zu Chalkline – es ist integriert und muss nicht eingerichtet werden. Der Watcher übernimmt die Wahl von dort.</translation>
    </message>
</context>
<context>
    <name>WatcherTray</name>
    <message>
        <location filename="../watch/tray.py" line="812"/>
        <location filename="../watch/tray.py" line="826"/>
        <location filename="../watch/tray.py" line="1046"/>
        <source>Snipwright Watcher</source>
        <translation>Snipwright Watcher</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="827"/>
        <source>Watching for recordings. Right-click the tray icon for options.</source>
        <translation>Überwachung auf Aufnahmen läuft. Klicken Sie mit der rechten Maustaste auf das Tray-Icon für Optionen.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="841"/>
        <source>Scan now</source>
        <translation>Jetzt scannen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="843"/>
        <location filename="../watch/tray.py" line="862"/>
        <source>Pause</source>
        <translation>Pause</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="846"/>
        <location filename="../watch/tray.py" line="957"/>
        <location filename="../watch/tray.py" line="964"/>
        <source>Launch Snipwright</source>
        <translation>Snipwright starten</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="848"/>
        <source>Open output folder</source>
        <translation>Ausgabeordner öffnen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="850"/>
        <source>Edit ignore list…</source>
        <translation>Ignorierliste bearbeiten…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="852"/>
        <source>Settings…</source>
        <translation>Einstellungen…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="855"/>
        <source>Quit</source>
        <translation>Beenden</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="862"/>
        <source>Resume</source>
        <translation>Fortsetzen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="908"/>
        <source>Scanning…</source>
        <translation>Scannen…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="925"/>
        <source>Pausing — finishing the current file…</source>
        <translation>Anhalten — aktuelle Datei wird fertiggestellt…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="927"/>
        <location filename="../watch/tray.py" line="1030"/>
        <source>Paused.</source>
        <translation>Pausiert.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="929"/>
        <source>Watching.</source>
        <translation>Überwachung läuft.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="958"/>
        <source>Couldn&apos;t find the editor (main.py) next to the watcher.</source>
        <translation>Der Editor (main.py) konnte neben dem Watcher nicht gefunden werden.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="964"/>
        <source>Couldn&apos;t launch the editor:
%s</source>
        <translation>Der Editor konnte nicht gestartet werden:
%s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1012"/>
        <source>Scanning %s…</source>
        <translation>Scanne %s…</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1016"/>
        <source>Commercials found</source>
        <translation>Werbung gefunden</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1017"/>
        <source>%s: %s break(s). Project ready in the Batch Manager.</source>
        <translation>%s: %s Unterbrechung(en). Projekt bereit im Batch-Manager.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1021"/>
        <source>Scan problem</source>
        <translation>Problem beim Scannen</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1021"/>
        <source>%s: %s</source>
        <translation>%s: %s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1027"/>
        <source>Scan failed: %s</source>
        <translation>Scan fehlgeschlagen: %s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1035"/>
        <source>Last scan: %s new recording(s), %s with commercials.</source>
        <translation>Letzter Scan: %s neue Aufnahme(n), %s mit Werbung.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1042"/>
        <source>Removed %d stale ignore entry/entries: %s.</source>
        <translation>%d veraltete(n) Ignorier-Eintrag/Einträge entfernt: %s.</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="1057"/>
        <source>Snipwright Watcher
%s</source>
        <translation>Snipwright Watcher
%s</translation>
    </message>
    <message>
        <location filename="../watch/tray.py" line="897"/>
        <source>Comskip isn&apos;t set - open Settings and configure it in the editor first, or switch to Chalkline there.</source>
        <translation>Comskip ist nicht festgelegt – öffnen Sie die Einstellungen und konfigurieren Sie es zuerst im Editor, oder wechseln Sie dort zu Chalkline.</translation>
    </message>
</context>
</TS>
