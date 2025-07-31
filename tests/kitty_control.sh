kitty --listen-on=unix:/tmp/mykitty &
sleep 1
kitten @ --to unix:/tmp/mykitty send-text "cd ~/Clone/listpick/src"
kitten @ --to unix:/tmp/mykitty send-key return
kitten @ --to unix:/tmp/mykitty send-text "python -m listpick.listpick_app -g ~/Clone/listpick/examples/list_files.toml"
kitten @ --to unix:/tmp/mykitty send-key return

sleep 1
kitten @ --to unix:/tmp/mykitty send-text "jjjjJ"
sleep 1
kitten @ --to unix:/tmp/mykitty send-text "/"
kitten @ --to unix:/tmp/mykitty send-text "\."
kitten @ --to unix:/tmp/mykitty send-key return
kitten @ --to unix:/tmp/mykitty send-key F5
