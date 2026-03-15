package ai.chappie.app.ui

import androidx.compose.runtime.Composable
import ai.chappie.app.MainViewModel
import ai.chappie.app.ui.chat.ChatSheetContent

@Composable
fun ChatSheet(viewModel: MainViewModel) {
  ChatSheetContent(viewModel = viewModel)
}
